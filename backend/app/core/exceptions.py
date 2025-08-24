"""
Custom Exceptions for the Application

Defines custom exception classes for business logic errors.
"""


class TagAlreadyExistsError(Exception):
    """Exception raised when trying to create a tag that already exists"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class TagNotFoundError(Exception):
    """Exception raised when trying to access a tag that doesn't exist"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InvalidTagNameError(Exception):
    """Exception raised when tag name is invalid"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
