class CustomError(Exception):
    """
    Custom exception class for handling errors with an optional error code.

    Parameters
    ----------
    message : str
        The error message describing the exception.
    code : any, optional
        An optional error code associated with the exception.
    """

    def __init__(self, message, code=None):
        """
        Initialize the custom error with a message and an optional error code.

        Parameters
        ----------
        message : str
            The error message describing the exception.
        code : any, optional
            An optional error code associated with the exception.
        """
        super().__init__(message)
        self.code = code