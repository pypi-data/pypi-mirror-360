"""bisslog_exception_handler_supabase decorator implementation"""
from functools import wraps

from bisslog.exceptions.external_interactions_errors import (
    InvalidDataExtException, IntegrityErrorExtException, ProgrammingErrorExtException,
    ConfigurationExtException, TimeoutExtException, ConnectionExtException,
    OperationalErrorExtException, ExternalInteractionError
)

from httpx import HTTPStatusError, TimeoutException, RequestError


def bisslog_exc_mapper_supabase(func):
    """Decorator to catch and map Supabase-specific exceptions to Bisslog external errors."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except HTTPStatusError as error:
            status = error.response.status_code
            if status == 400:
                raise InvalidDataExtException from error
            elif status == 401:
                raise ConfigurationExtException from error
            elif status == 403:
                raise ProgrammingErrorExtException from error
            elif status == 404:
                raise ProgrammingErrorExtException from error
            elif status == 409:
                raise IntegrityErrorExtException from error
            elif 500 <= status < 600:
                raise OperationalErrorExtException from error
            else:
                raise ExternalInteractionError from error

        except TimeoutException as error:
            raise TimeoutExtException from error

        except RequestError as error:
            raise ConnectionExtException from error

        except Exception as error:
            raise ExternalInteractionError from error

    return wrapper
