class ModelWDockerException(Exception):
    """Base exception for all the package"""


class UserException(ModelWDockerException):
    """Exception raised when user input (in the general sense) is invalid."""
