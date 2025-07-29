from enum import Enum
from typing import Optional


class HTTPStatus(Enum):
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    TOO_MANY_REQUESTS = 429
    CLIENT_CLOSED_REQUEST = 499
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503
    TIMEOUT = 504

    def __str__(self) -> str:
        return f"HTTPStatus.{self.name}({self.value})"

    @staticmethod
    def for_code(code: int) -> Optional['HTTPStatus']:
        """returns the HTTPStatus with the given http status code.
        """
        for s in HTTPStatus:
            if s.value == code:
                return s
        return None