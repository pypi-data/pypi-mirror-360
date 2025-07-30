class QueryBuilderException(Exception):
    """Errors related to Query Builder"""


class DatabaseResultError(BaseException):
    """Errors related to database results"""


class MultipleRowsError(DatabaseResultError):
    """Multiple rows returned instead of 1 or 0"""


class NoRowsError(DatabaseResultError):
    """No rows were returned"""
