class ApplicationException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ResourceNotFoundException(ApplicationException):
    def __init__(self, resource_name: str, resource_id: str):
        super().__init__(
            message=f"{resource_name} con id '{resource_id}' no encontrado",
            status_code=404,
        )


class ValidationException(ApplicationException):
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class DuplicateResourceException(ApplicationException):
    def __init__(self, resource_name: str, field: str, value: str):
        super().__init__(
            message=f"{resource_name} con {field} '{value}' ya existe",
            status_code=409,
        )