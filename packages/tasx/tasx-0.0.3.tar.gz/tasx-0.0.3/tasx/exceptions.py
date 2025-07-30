class TasxRegistryAPIError(Exception):
    """General exception for TASX Registry API errors."""
    pass


class TasxRunnerAPIError(Exception):
    pass


class TaskNotFoundError(TasxRegistryAPIError):
    """Exception raised when a task is not found."""
    pass


class TaskRunNotFoundError(TasxRunnerAPIError):
    pass