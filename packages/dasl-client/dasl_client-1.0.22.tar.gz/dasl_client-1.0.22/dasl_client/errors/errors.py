import json
from collections.abc import Callable
from contextlib import contextmanager

from dasl_api import ApiException
from urllib3.exceptions import MaxRetryError, RequestError


class ConflictError(Exception):
    """
    Simple exception wrapper for 409 errors returned from the API
    """

    def __init__(self, resource: str, identifier: str, message: str) -> None:
        self.resource = resource
        self.identifier = identifier
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"Conflict: resource_type='{self.resource}' identifier='{self.identifier}' message='{self.message}'"


class NotFoundError(Exception):
    """
    Simple exception wrapper for 404 errors returned from the API
    """

    def __init__(self, identifier: str, message: str) -> None:
        self.identifier = identifier
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"NotFound: identifier='{self.identifier}' message='{self.message}'"


class BadRequestError(Exception):
    """
    Simple exception wrapper for 400 errors returned from the API
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"BadRequest: message='{self.message}'"


class UnauthorizedError(Exception):
    """
    Simple exception wrapper for 401 errors returned from the API
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"Unauthorized: message='{self.message}'"


class ForbiddenError(Exception):
    """
    Simple exception wrapper for 403 errors returned from the API
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"Forbidden: message='{self.message}'"


def handle_errors(f: Callable) -> Callable:
    """
    A decorator that handles errors returned from the API.

    :param f: the function that could return an API error
    :return: The output from the callable 'f'. If an Api error was raise,
             re-cast it to a library error before re-raising.
    """

    def error_handler(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ApiException as e:
            body = json.loads(e.body)
            if e.status == 400:
                raise BadRequestError(body["message"])
            if e.status == 401:
                raise BadRequestError(body["message"])
            if e.status == 403:
                raise ForbiddenError(body["message"])
            if e.status == 404:
                raise NotFoundError(body["identifier"], body["message"])
            if e.status == 409:
                raise ConflictError(
                    body["resourceType"], body["identifier"], body["message"]
                )
            else:
                raise e
        except Exception as e:
            raise e

    return error_handler


@contextmanager
def error_handler():
    """
    A context manager that handles errors returned from the API.

    Within the context, if an API error is raised, it is re-cast to a library
    error before re-raising.
    """
    try:
        yield
    except ApiException as e:
        body = json.loads(e.body)
        if e.status == 400:
            raise BadRequestError(body["message"])
        if e.status == 401:
            raise BadRequestError(body["message"])
        if e.status == 403:
            raise ForbiddenError(body["message"])
        if e.status == 404:
            raise NotFoundError(body["identifier"], body["message"])
        if e.status == 409:
            raise ConflictError(
                body["resourceType"], body["identifier"], body["message"]
            )
        else:
            raise e
    except Exception as e:
        raise e
