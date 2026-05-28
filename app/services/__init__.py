from app.core.logging import LoggerMixin


class ServiceError(Exception):
    pass


class BaseService(LoggerMixin):
    pass
