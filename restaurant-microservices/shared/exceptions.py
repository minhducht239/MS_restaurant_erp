"""
Custom exceptions for microservices
"""


class ServiceException(Exception):
    """Base exception for service errors"""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationException(ServiceException):
    """Authentication related errors"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationException(ServiceException):
    """Authorization related errors"""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status_code=403)


class ValidationException(ServiceException):
    """Validation errors"""
    
    def __init__(self, message: str, errors: dict = None):
        self.errors = errors or {}
        super().__init__(message, status_code=400)


class NotFoundException(ServiceException):
    """Resource not found errors"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ConflictException(ServiceException):
    """Conflict errors (e.g., duplicate entries)"""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409)
