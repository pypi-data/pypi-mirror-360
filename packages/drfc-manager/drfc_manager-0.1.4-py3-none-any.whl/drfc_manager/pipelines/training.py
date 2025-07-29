import time
from typing import Callable, Dict, Optional

from drfc_manager.types.env_vars import EnvVars
from gloe import If, transformer
from gloe.utils import forward
from drfc_manager.transformers.training import (
    create_sagemaker_temp_files,
    check_if_metadata_is_available,
    upload_hyperparameters,
    upload_metadata,
    upload_reward_function,
    upload_training_params_file,
    start_training,
    expose_config_envs_from_dataclass,
    check_training_logs_transformer,
)
from drfc_manager.transformers.general import (
    check_if_model_exists_transformer,
    copy_object,
    echo,
    forward_condition,
)
from drfc_manager.types.hyperparameters import HyperParameters
from drfc_manager.types.model_metadata import ModelMetadata
from drfc_manager.config_env import settings
from drfc_manager.utils.docker.docker_manager import DockerManager, DockerError
from drfc_manager.utils.minio.storage_manager import MinioStorageManager
from drfc_manager.models.model_operations import (
    create_clone_config,
    generate_model_name,
)
from drfc_manager.models.storage_operations import (
    check_model_exists,
    delete_model,
    upload_model_data,
)
from drfc_manager.models.env_operations import create_env_config, apply_env_config
from drfc_manager.models.data_extraction import extract_model_data
from drfc_manager.utils.logging import logger, setup_logging

storage_manager = MinioStorageManager(settings)
env_vars = EnvVars()

@transformer
def sleep_15_seconds(_):
    """Sleep for 15 seconds before checking logs"""
    time.sleep(15)
    return _


def _check_critical_vars(env_vars: EnvVars):
    critical_vars = {
        'DR_SIMAPP_SOURCE': env_vars.DR_SIMAPP_SOURCE,
        'DR_SIMAPP_VERSION': env_vars.DR_SIMAPP_VERSION
    }
    
    missing_vars = [var for var, value in critical_vars.items() if not value]
    if missing_vars:
        logger.error(f"Missing critical environment variables: {', '.join(missing_vars)}")
        logger.error(f"Current environment state: {critical_vars}")
        raise DockerError(f"Missing critical environment variables: {', '.join(missing_vars)}")
    

    logger.info("Environment variables loaded:")
    logger.info(f"DR_SIMAPP_SOURCE: {env_vars.DR_SIMAPP_SOURCE}")
    logger.info(f"DR_SIMAPP_VERSION: {env_vars.DR_SIMAPP_VERSION}")
    
    
    
    
def train_pipeline(
    model_name: str,
    hyperparameters: HyperParameters,
    model_metadata: ModelMetadata,
    reward_function: Callable[[Dict], float],
    overwrite: bool = False,
    check_logs_after_start: bool = False,
    reward_function_code: Optional[str] = None,
    quiet: bool = True,
    env_vars: Optional[EnvVars] = None,
):
    """
    Orchestrates the training pipeline (using original structure).

    Args:
        model_name (str): Name of the model to be trained.
        hyperparameters (HyperParameters): Training hyperparameters.
        model_metadata (ModelMetadata): Model metadata.
        reward_function (Callable[[Dict], float]): Reward function.
        overwrite (bool, optional): Overwrite existing model data. Defaults to False.
        check_logs_after_start (bool, optional): Check logs after stack start. Defaults to False.
        reward_function_code (Optional[str], optional): Reward function code. Defaults to None.
        quiet (bool, optional): If True, suppress console output. Defaults to True.
        env_vars (Optional[EnvVars], optional): Environment variables to update. Defaults to None.
    """
    # Get or create singleton instance and set up environment variables first
    env_vars_instance = EnvVars()
    
    if env_vars:
        env_vars_instance.update(**{k: v for k, v in env_vars.__dict__.items() if not k.startswith('_')})
        env_vars_instance.load_to_environment()

    env_vars_instance.update(DR_LOCAL_S3_MODEL_PREFIX=model_name)
    env_vars_instance.load_to_environment()
    
    _check_critical_vars(env_vars_instance)
    run_id = env_vars_instance.DR_RUN_ID
    setup_logging(run_id=run_id, model_name=model_name, quiet=quiet)

    _custom_files_folder = settings.minio.custom_files_folder
    _bucket_name = env_vars_instance.MINIO_BUCKET_NAME

    reward_function_obj_location_custom = f"{_custom_files_folder}/reward_function.py"
    reward_function_obj_location_model = f"{model_name}/reward_function.py"

    model_data_to_custom_files = forward[None]() >> (
        (
            upload_hyperparameters(hyperparameters=hyperparameters),
            upload_metadata(model_metadata=model_metadata),
            upload_reward_function(
                reward_function=reward_function_code or reward_function
            ),
        )
    )

    check_logs_step = (
        forward[None]() >> sleep_15_seconds >> check_training_logs_transformer
    )

    training_start_pipeline = (
        create_sagemaker_temp_files
        >> check_if_metadata_is_available
        >> check_if_model_exists_transformer(model_name=model_name, overwrite=overwrite)
        >> forward_condition.Then(
            echo(
                data=None,
                message=f"Model prefix 's3://{_bucket_name}/{model_name}' exists and overwrite=False. Aborting.",
            )
        ).Else(
            model_data_to_custom_files
            >> echo(data=None, message="Data uploaded successfully to custom files")
            >> copy_object(
                source_object_name=reward_function_obj_location_custom,
                dest_object_name=reward_function_obj_location_model,
            )
            >> echo(
                data=None,
                message=f"The reward function copied successfully to models folder at {reward_function_obj_location_model}",
            )
            >> upload_training_params_file(model_name=model_name)
            >> echo(
                data=None,
                message="Upload successfully the RoboMaker training configurations",
            )
            # >> upload_ip_config(model_name=model_name)
            >> expose_config_envs_from_dataclass(
                model_name=model_name, bucket_name=_bucket_name
            )
            >> echo(data=None, message="Starting model training")
            >> start_training
            >> echo(data=None, message="Docker stack started.")
            >> If(lambda _: check_logs_after_start)
            .Then(check_logs_step >> echo(data=None, message="Log check performed."))
            .Else(echo(data=None, message="Skipping log check."))  # type: ignore[arg-type]
        )
    )

    logger.info(
        f"Starting training pipeline for model: {model_name}, Run ID: {run_id}"
    )
    training_start_pipeline(None)
    logger.info("Training pipeline finished.")


def stop_training_pipeline():
    """
    Stops the currently running DeepRacer training Docker stack.

    Uses the run_id from the current settings (or DR_RUN_ID env var)
    to identify the correct Docker Compose project.
    """
    logger.info('Stopping training stack via drfc-manager (matching dr-stop-training)...')
    try:
        dm = DockerManager(settings)
        # Reconstruct compose files used at startup
        compose_paths, _ = dm._prepare_compose_files(dm.env_vars.DR_WORKERS)
        sep = settings.docker.dr_docker_file_sep
        compose_str = sep.join(compose_paths)
        if dm.env_vars.DR_DOCKER_STYLE.lower() == 'swarm':
            dm.remove_stack(dm.project_name)
        else:
            dm.compose_down(dm.project_name, compose_str, remove_volumes=False)
        logger.info('Training stack stopped successfully.')
    except DockerError as e:
        logger.error(f'Error stopping training stack: {e}')
    except Exception as e:
        logger.error(f'Unexpected error stopping training stack: {type(e).__name__}: {e}')


def clone_pipeline(
    source_model_name: str,
    new_model_name: Optional[str] = None,
    delimiter: str = "-",
    wipe_target: bool = False,
    custom_hyperparameters: Optional[HyperParameters] = None,
    custom_model_metadata: Optional[ModelMetadata] = None,
    custom_reward_function: Optional[Callable[[Dict], float]] = None,
    check_logs_after_start: bool = False,
    skip_training: bool = False,
    quiet: bool = True,
) -> str:
    """Functional pipeline for cloning a model."""
    config = create_clone_config(
        source_model_name,
        new_model_name,
        delimiter,
        wipe_target,
        custom_hyperparameters,
        custom_model_metadata,
        custom_reward_function,
        check_logs_after_start,
        skip_training,
    )

    target_name = generate_model_name(
        config.source_name, config.target_name, config.delimiter
    )

    if not check_model_exists(storage_manager, config.source_name):
        raise ValueError(f"Source model '{config.source_name}' does not exist")

    if check_model_exists(storage_manager, target_name):
        if not config.wipe_target:
            raise ValueError(
                f"Target model '{target_name}' exists and wipe_target=False"
            )
        delete_model(storage_manager, target_name)

    env_config = create_env_config(config.source_name, target_name)
    apply_env_config(env_config)

    model_data = extract_model_data(
        storage_manager,
        config.source_name,
        config.custom_hyperparameters,
        config.custom_metadata,
        config.custom_reward_function,
    )

    upload_model_data(storage_manager, model_data)

    if not config.skip_training:
        train_pipeline(
            model_name=target_name,
            hyperparameters=model_data.hyperparameters,
            model_metadata=model_data.metadata,
            reward_function=model_data.reward_function,
            overwrite=True,
            check_logs_after_start=config.check_logs,
            reward_function_code=model_data.reward_code,
            quiet=quiet,
        )

    return target_name
