# your_project_root/app/core/exceptions.py
class AppException(Exception):
    """Base application exception."""
    status_code = 500
    message = "An unexpected error occurred."

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__(message)
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class NotFoundError(AppException):
    status_code = 404
    message = "Resource not found."

class BadRequestError(AppException):
    status_code = 400
    message = "Bad request."

class ForbiddenError(AppException):
    status_code = 403
    message = "Forbidden."

class ValidationError(AppException):
    status_code = 422 # Unprocessable Entity
    message = "Validation error."

    def __init__(self, message="Validation error.", errors=None, status_code=None, payload=None):
        super().__init__(message, status_code, payload)
        self.errors = errors # Dictionary of field errors

    def to_dict(self):
        rv = super().to_dict()
        if self.errors:
            rv['errors'] = self.errors
        return rv