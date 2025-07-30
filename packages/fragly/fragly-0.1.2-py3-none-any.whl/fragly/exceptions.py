class FraglyFragmentAPIError(Exception):
    """Base exception for PepeFragment Fragment API errors."""


class InvalidUsernameError(FraglyFragmentAPIError):
    """Raised when the username is invalid or not found."""


class InsufficientBalanceError(FraglyFragmentAPIError):
    """Raised when the user has insufficient balance."""