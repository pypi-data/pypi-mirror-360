from typing import List, Optional


class DockerError(Exception):
    """Custom exception for Docker-related errors."""

    def __init__(
        self,
        message: str,
        command: Optional[List[str]] = None,
        stderr: Optional[str] = None,
    ):
        super().__init__(message)
        self.command = command
        self.stderr = stderr

    def __str__(self):
        msg = super().__str__()
        if self.command:
            msg += f"\nCommand: {' '.join(self.command)}"
        if self.stderr:
            msg += f"\nStderr:\n{self.stderr}"
        return msg
