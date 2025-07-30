class BaseError(Exception):
    pass


class NotFoundError(BaseError):
    pass


class DatabaseConnectionError(BaseError):
    pass


class DatabaseQueryError(BaseError):
    pass


class InvalidArgumentError(BaseError):
    pass


class DuplicateObjectError(BaseError):
    pass


class DatabaseConfigError(BaseError):
    pass


class ExternalError(BaseError):
    pass


class ConnectionNotInitialized(BaseError):
    pass


class InsertionError(BaseError):
    pass


class UpdateError(BaseError):
    pass


class DeletionError(BaseError):
    pass


class DuplicateKeyError(BaseError):
    pass


class AggregationError(BaseError):
    pass


class QueryExecutionError(BaseError):
    pass


class RedisConnectionError(BaseError):
    pass
