"""Кастомные исключения для r00docker."""

class DockerError(Exception):
    """Базовое исключение для ошибок r00docker."""
    pass

class ContainerNotFoundError(DockerError):
    """Контейнер не найден."""
    pass

class ImageNotFoundError(DockerError):
    """Образ не найден."""
    pass

class DockerOperationError(DockerError):
    """Общая ошибка при выполнении операции Docker."""
    pass

class DockerAuthenticationError(DockerError):
    """Ошибка аутентификации (например, при push/login)."""
    pass