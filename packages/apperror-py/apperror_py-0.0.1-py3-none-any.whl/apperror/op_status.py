from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional

from attr import dataclass

from apperror.http_status import HTTPStatus


class Code(Enum):
    """The set of canonical operation status codes.

    Sometimes multiple error codes may apply. Services should return the most specific error
    code that applies. For example, prefer `CodeOutOfRange` over `CodeFailedPrecondition` if both codes
    apply. Similarly prefer `CodeNotFound` or `CodeAlreadyExists` over `CodeFailedPrecondition`.
    """

    # OK not an error; returned on success.
    # HTTP Mapping: 200 OK
    OK = 0

    # Cancelled means the operation was cancelled, typically by the caller.
    # HTTP Mapping: 499 Client Closed Request
    OP_CANCELLED = 1

    # Unknown error. For example, this error may be returned when
    # a Status value received from another address space belongs to
    # an error space that is not known in this address space. Also
    # errors raised by APIs that do not return enough error information
    # may be converted to this error.
    # HTTP Mapping: 500 Internal Server Error
    UNKNOWN_ERROR = 2

    # IllegalInput means that the client specified an illegal input.
    # Note that this differs from FailedPrecondition. IllegalInput indicates
    # inputs that are problematic regardless of the state of the system
    # (e.g., a malformed file name).
    # HTTP Mapping: 400 Bad Request
    ILLEGAL_INPUT = 3

    # TIMEOUT means the deadline expired before the operation could complete.
    # For operations that change the state of the system, this error may be returned
    # even if the operation has completed successfully. For example, a successful
    # response from a server could have been delayed long enough for the deadline
    # to expire.
    # HTTP Mapping: 504 Gateway Timeout
    TIMEOUT = 4

    # NotFound means that some requested entity (e.g., file or directory) was not found.
    # Note to server developers: if a request is denied for an entire class
    # of users, such as gradual feature rollout or undocumented allowlist,
    # NotFound may be used. If a request is denied for some users within
    # a class of users, such as user-based access control, PermissionDenied
    # must be used.
    # HTTP Mapping: 404 Not Found
    NOT_FOUND = 5

    # AlreadyExists means that the entity that a client attempted to create
    # (e.g., file or directory) already exists.
    # HTTP Mapping: 409 Conflict
    ALREADY_EXISTS = 6

    # PermissionDenied means the caller does not have permission to execute the specified
    # operation. PermissionDenied must not be used for rejections caused by
    # exhausting some resource (use ResourceExhausted instead for those errors).
    # PermissionDenied must not be used if the caller can not be identified
    # (use Unauthenticated instead for those errors). This error code does not
    # imply the request is valid or the requested entity exists or satisfies
    # other pre-conditions.
    # HTTP Mapping: 403 Forbidden
    PERMISSION_DENIED = 7

    # ResourceExhausted means that some resource has been exhausted, perhaps
    # a per-user quota, or perhaps the entire file system is out of space.
    # HTTP Mapping: 429 Too Many Requests
    RESOURCE_EXHAUSTED = 8

    # FailedPrecondition means that the operation was rejected because the system
    # is not in a state required for the operation's execution. For example,
    # the directory to be deleted is non-empty, a rmdir operation is applied to
    # a non-directory, etc.
    # Service implementors can use the following guidelines to decide
    # between FailedPrecondition, Aborted, and Unavailable:
    #  (a) Use Unavailable if the client can retry just the failing call.
    #  (b) Use Aborted if the client should retry at a higher level. For
    #      example, when a client-specified test-and-set fails, indicating the
    #      client should restart a read-modify-write sequence.
    #  (c) Use FailedPrecondition if the client should not retry until
    #      the system state has been explicitly fixed. For example, if a "rmdir"
    #      fails because the directory is non-empty, FailedPrecondition
    #      should be returned since the client should not retry unless
    #      the files are deleted from the directory.
    # HTTP Mapping: 400 Bad Request
    FAILED_PRECONDITION = 9

    # Aborted means that the operation was aborted, typically due to a concurrency
    # issue such as a sequencer check failure or transaction abort.
    # See the guidelines above for deciding between FailedPrecondition,
    # Aborted, and Unavailable.
    # HTTP Mapping: 409 Conflict
    OP_ABORTED = 10

    # OutOfRange means that the operation was attempted past the valid range.
    # E.g., seeking or reading past end-of-file.
    # Unlike InvalidArgument, this error indicates a problem that may
    # be fixed if the system state changes. For example, a 32-bit file
    # system will generate InvalidArgument if asked to read at an
    # offset that is not in the range [0,2^32-1], but it will generate
    # OutOfRange if asked to read from an offset past the current
    # file size.
    # There is a fair bit of overlap between FailedPrecondition and
    # OutOfRange. We recommend using OutOfRange (the more specific
    # error) when it applies so that callers who are iterating through
    # a space can easily look for an OutOfRange error to detect when
    # they are done.
    # HTTP Mapping: 400 Bad Request
    OUT_OF_RANGE = 11

    # Unimplemented means that the operation is defined, but not implemented
    # or not supported/enabled in this service.
    # HTTP Mapping: 501 Not Implemented
    UNIMPLEMENTED = 12

    # Internal error means that some invariants expected by the underlying system
    # have been broken. This error code is reserved for serious errors.
    # HTTP Mapping: 500 Internal Server Error
    INTERNAL_ERROR = 13

    # Unavailable means that the service is currently unavailable. This is
    # most likely a transient condition, which can be corrected by retrying
    # with a backoff. Note that it is not always safe to retry
    # non-idempotent operations.
    # See the guidelines above for deciding between FailedPrecondition,
    # Aborted, and Unavailable.
    # HTTP Mapping: 503 Service Unavailable
    UNAVAILABLE = 14

    # IllegalState means illegal data found in datastore, unrecoverable data loss or corruption and so on.
    # HTTP Mapping: 500 Internal Server Error
    ILLEGAL_STATE = 15

    # Unauthenticated means that the request does not have valid authentication
    # credentials for the operation.
    # HTTP Mapping: 401 Unauthorized
    UNAUTHENTICATED = 16

    # The arguments passed to an operation within the program is illegal.
    # HTTP Mapping: 500 Internal Server Error
    ILLEGAL_ARG = 29

    # AuthorizationExpired means a user's authorization expired, and it is
    # needed to log-in again and reauthorize.
    # HTTP Mapping: 401 Unauthorized
    AUTHORIZATION_EXPIRED = 30

    def __str__(self) -> str:
        return f"{self.name}({self.value})"


_code_to_http_status = {
    Code.OK: HTTPStatus.OK,
    Code.ILLEGAL_INPUT: HTTPStatus.BAD_REQUEST,
    Code.FAILED_PRECONDITION: HTTPStatus.BAD_REQUEST,
    Code.OUT_OF_RANGE: HTTPStatus.BAD_REQUEST,
    Code.UNAUTHENTICATED: HTTPStatus.UNAUTHORIZED,
    Code.PERMISSION_DENIED: HTTPStatus.FORBIDDEN,
    Code.NOT_FOUND: HTTPStatus.NOT_FOUND,
    Code.OP_ABORTED: HTTPStatus.CONFLICT,
    Code.ALREADY_EXISTS: HTTPStatus.CONFLICT,
    Code.RESOURCE_EXHAUSTED: HTTPStatus.TOO_MANY_REQUESTS,
    Code.OP_CANCELLED: HTTPStatus.CLIENT_CLOSED_REQUEST,
    Code.ILLEGAL_STATE: HTTPStatus.INTERNAL_SERVER_ERROR,
    Code.UNKNOWN_ERROR: HTTPStatus.INTERNAL_SERVER_ERROR,
    Code.INTERNAL_ERROR: HTTPStatus.INTERNAL_SERVER_ERROR,
    Code.UNIMPLEMENTED: HTTPStatus.NOT_IMPLEMENTED,
    Code.UNAVAILABLE: HTTPStatus.SERVICE_UNAVAILABLE,
    Code.TIMEOUT: HTTPStatus.TIMEOUT,
    Code.AUTHORIZATION_EXPIRED: HTTPStatus.UNAUTHORIZED,
    Code.ILLEGAL_ARG: HTTPStatus.INTERNAL_SERVER_ERROR,
}


def http_status_for(code: Code) -> Optional[HTTPStatus]:
    """returns the HTTPStatus which the given OpStatusCode is mapped to."""
    return _code_to_http_status[code]


class Case(ABC):
    """represents a specific error condition.
    For example: purchase_limit_exceeded, insufficient_inventory.
    """

    def __init__(self):
        pass

    @abstractmethod
    def identifier(self) -> str:
        """returns a string that uniquely identifies this error case.
        It can be a numerical value or a descriptive title/name.
        For example, two numerical values: 1000, 1_1_1000;
        a descriptive title/name: purchase_limit_exceeded.
        """
        pass

    def __str__(self) -> str:
        return f"{self.identifier()}"


class StrCase(Case):
    """a specific error condition identified by some words or a phrase.
    For example: purchase_limit_exceeded, insufficient_inventory.
    """

    def __init__(self, identifier: str):
        self._identifier = identifier

    def identifier(self) -> str:
        return self._identifier


class Status:
    """represents an operation status."""

    _code: Code
    _case: Optional[Case] = None
    # A developer-facing error message, which should be in English. Any
    # user-facing error message should be localized and sent in the
    # details field, or localized by the client.
    _message: str = ""
    _details: Any = None

    def __init__(
        self,
        code: Code,
        case: Optional[Case] = None,
        message: str = "",
        details: Any = None,
    ):
        self._code = code
        self._case = case
        self._message = message
        self._details = details

    @property
    def code(self) -> Code:
        return self._code

    @property
    def case(self) -> Optional[Case]:
        return self._case

    @property
    def message(self) -> str:
        return self._message

    @property
    def details(self) -> Any:
        return self._details

    def with_msg(self, msg: str) -> "Status":
        """returns a derived instance of this Status with the given message.
        Leading and trailing whitespace is removed.
        """
        msg = msg.strip()
        return Status(
            code=self._code, case=self._case, message=msg, details=self._details
        )

    def with_case(self, case: Case) -> "Status":
        """returns a derived instance of this Status with the given case."""
        return Status(
            code=self._code, case=case, message=self._message, details=self._details
        )

    def with_case_and_msg(self, case: Case, msg: str) -> "Status":
        """returns a derived instance of this Status with the given case and message.
        Leading and trailing whitespace is removed.
        """
        msg = msg.strip()
        return Status(code=self._code, case=case, message=msg, details=self._details)

    def with_details(self, details: Any) -> "Status":
        """returns a derived instance of this Status with the given details."""
        return Status(
            code=self._code, case=self._case, message=self._message, details=details
        )

    def add_more_ctx_to_msg(self, more_ctx: str) -> None:
        """add more contextual information about current status to message."""
        if self._message:
            self._message = f"{self._message} {more_ctx}"
        else:
            self._message = more_ctx

    def is_ok(self) -> bool:
        """tells if this status is OK, i.e., not an error"""
        return self._code == Code.OK

    def simple_str(self) -> str:
        parts = []
        if self._code:
            parts.append(f"code={self._code}")
        if self._case:
            parts.append(f"case={self._case}")
        if self._message:
            parts.append(f"message='{self._message}'")
        return f"({', '.join(parts)})"

    def __str__(self) -> str:
        """Returns the string representation of the status in object style."""
        parts = []
        if self._code:
            parts.append(f"code={self._code}")
        if self._case:
            parts.append(f"case={self._case}")
        if self._message:
            parts.append(f"message='{self._message}'")
        if self._details is not None:
            parts.append(f"details={self._details}")
        return f"({', '.join(parts)})"

    def __eq__(self, that: "Status") -> bool:
        if not isinstance(that, Status):
            return False
        if self._case is None and that._case is None:
            return self._code == that._code
        if self._case is None or that._case is None:
            return False
        return (
            self._code == that._code
            and self._case.identifier() == that._case.identifier()
        )

    @staticmethod
    def new_from_http_resp(
        status_code: int,
        resp: Optional["Response"] = None,
        req: Optional["Request"] = None,
    ) -> "Status":
        op_status: Optional[Status] = None
        http_status = HTTPStatus.for_code(status_code)
        if http_status is None:
            op_status = STATUS_UNKNOWN_ERROR
        else:
            op_status = HTTP_STATUS_TO_STATUS.get(http_status) or STATUS_UNKNOWN_ERROR

        if req is not None or resp is not None:
            details = {}
            if req is not None:
                details["req"] = req
            if resp is not None:
                details["resp"] = resp
            op_status = op_status.with_details(details)

        return op_status


CODE_TO_STATUS: Dict[Code, Status] = {code: Status(code=code) for code in Code}

# A pseudo-enum of Status instances mapped 1:1 with codes in Code. This simplifies construction
# patterns for derived instances of Status.

# The operation completed successfully.
STATUS_OK = CODE_TO_STATUS[Code.OK]

# The operation was cancelled (typically by the caller).
STATUS_OP_CANCELLED = CODE_TO_STATUS[Code.OP_CANCELLED]

# Unknown error. See Code.UNKNOWN.
STATUS_UNKNOWN_ERROR = CODE_TO_STATUS[Code.UNKNOWN_ERROR]

# Client specified an illegal input. See Code.ILLEGAL_INPUT.
STATUS_ILLEGAL_INPUT = CODE_TO_STATUS[Code.ILLEGAL_INPUT]

# Deadline expired before operation could complete. See Code.TIMEOUT.
STATUS_TIMEOUT = CODE_TO_STATUS[Code.TIMEOUT]

# Some requested entity (e.g., file or directory) was not found.
STATUS_NOT_FOUND = CODE_TO_STATUS[Code.NOT_FOUND]

# Some entity that we attempted to create (e.g., file or directory) already exists.
STATUS_ALREADY_EXISTS = CODE_TO_STATUS[Code.ALREADY_EXISTS]

# The caller does not have permission to execute the specified operation. See Code.PERMISSION_DENIED.
STATUS_PERMISSION_DENIED = CODE_TO_STATUS[Code.PERMISSION_DENIED]

# The request does not have valid authentication credentials for the operation.
STATUS_UNAUTHENTICATED = CODE_TO_STATUS[Code.UNAUTHENTICATED]

# Some resource has been exhausted, perhaps a per-user quota, or perhaps the entire file system
# is out of space.
STATUS_RESOURCE_EXHAUSTED = CODE_TO_STATUS[Code.RESOURCE_EXHAUSTED]

# Operation was rejected because the system is not in a state required for the operation's
# execution. See Code.FAILED_PRECONDITION.
STATUS_FAILED_PRECONDITION = CODE_TO_STATUS[Code.FAILED_PRECONDITION]

# The operation was aborted, typically due to a concurrency issue like sequencer check failures,
# transaction aborts, etc. See Code.ABORTED.
STATUS_OP_ABORTED = CODE_TO_STATUS[Code.OP_ABORTED]

# Operation was attempted past the valid range. See Code.OUT_OF_RANGE.
STATUS_OUT_OF_RANGE = CODE_TO_STATUS[Code.OUT_OF_RANGE]

# Operation is not implemented or not supported/enabled in this service.
STATUS_UNIMPLEMENTED = CODE_TO_STATUS[Code.UNIMPLEMENTED]

# Internal errors. See Code.INTERNAL_ERROR.
STATUS_INTERNAL_ERROR = CODE_TO_STATUS[Code.INTERNAL_ERROR]

# The service is currently unavailable. See Code.UNAVAILABLE.
STATUS_UNAVAILABLE = CODE_TO_STATUS[Code.UNAVAILABLE]

# Illegal data found in datastore, unrecoverable data loss or corruption.
STATUS_ILLEGAL_STATE = CODE_TO_STATUS[Code.ILLEGAL_STATE]

# A user's authorization expired, and it is needed to log-in again and reauthorize.
STATUS_AUTHORIZATION_EXPIRED = CODE_TO_STATUS[Code.AUTHORIZATION_EXPIRED]

# The arguments passed to an operation within the program is illegal.
STATUS_ILLEGAL_ARG = CODE_TO_STATUS[Code.ILLEGAL_ARG]

# Mapping from HTTP status to operation status
HTTP_STATUS_TO_STATUS: Dict[HTTPStatus, Status] = {
    HTTPStatus.OK: STATUS_OK,
    HTTPStatus.BAD_REQUEST: STATUS_ILLEGAL_INPUT,
    HTTPStatus.UNAUTHORIZED: STATUS_UNAUTHENTICATED,
    HTTPStatus.FORBIDDEN: STATUS_PERMISSION_DENIED,
    HTTPStatus.NOT_FOUND: STATUS_NOT_FOUND,
    HTTPStatus.CONFLICT: STATUS_ALREADY_EXISTS,
    HTTPStatus.TOO_MANY_REQUESTS: STATUS_RESOURCE_EXHAUSTED,
    HTTPStatus.CLIENT_CLOSED_REQUEST: STATUS_OP_CANCELLED,
    HTTPStatus.INTERNAL_SERVER_ERROR: STATUS_INTERNAL_ERROR,
    HTTPStatus.NOT_IMPLEMENTED: STATUS_UNIMPLEMENTED,
    HTTPStatus.SERVICE_UNAVAILABLE: STATUS_UNAVAILABLE,
    HTTPStatus.TIMEOUT: STATUS_TIMEOUT,
}


@dataclass
class Request:
    url: str
    method: str
    headers: Any
    body: Any


@dataclass
class Response:
    status_code: int
    headers: Any
    body: Any
