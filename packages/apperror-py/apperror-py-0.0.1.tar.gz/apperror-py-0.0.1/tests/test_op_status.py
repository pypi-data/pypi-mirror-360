import pytest

from apperror.op_status import (
    STATUS_ALREADY_EXISTS,
    STATUS_AUTHORIZATION_EXPIRED,
    STATUS_FAILED_PRECONDITION,
    STATUS_ILLEGAL_INPUT,
    STATUS_ILLEGAL_STATE,
    STATUS_INTERNAL_ERROR,
    STATUS_NOT_FOUND,
    STATUS_OK,
    STATUS_OP_ABORTED,
    STATUS_OP_CANCELLED,
    STATUS_OUT_OF_RANGE,
    STATUS_PERMISSION_DENIED,
    STATUS_RESOURCE_EXHAUSTED,
    STATUS_TIMEOUT,
    STATUS_UNAUTHENTICATED,
    STATUS_UNAVAILABLE,
    STATUS_UNIMPLEMENTED,
    STATUS_UNKNOWN_ERROR,
    Case,
    Code,
    Response,
    Status,
)


class ErrorCase(Case):
    def __init__(self, identifier: str, op_status_code: Code):
        self._identifier = identifier
        self._op_status_code = op_status_code

    def identifier(self) -> str:
        return self._identifier


def test_code_no_duplicate_value():
    code_values = set()
    for code in Code:
        if code.value in code_values:
            pytest.fail(
                f"Code value duplication found: {code.name} has value {code.value}"
            )
        code_values.add(code.value)


def test_code_str_representation():
    assert str(Code.OK) == "OK(0)"
    assert str(Code.ILLEGAL_INPUT) == "ILLEGAL_INPUT(3)"
    assert str(Code.PERMISSION_DENIED) == "PERMISSION_DENIED(7)"
    assert str(Code.RESOURCE_EXHAUSTED) == "RESOURCE_EXHAUSTED(8)"
    assert str(Code.UNAUTHENTICATED) == "UNAUTHENTICATED(16)"
    assert str(Code.NOT_FOUND) == "NOT_FOUND(5)"


def test_status_equality():
    # Test equality of Status with same code
    status1 = Status(Code.OK)
    status2 = Status(Code.OK)
    assert status1 == status2

    # Test inequality of Status with different codes
    status3 = Status(Code.ILLEGAL_INPUT)
    assert status1 != status3

    # Test equality of Status with same case
    case1 = ErrorCase("ok", Code.OK)
    status4 = Status(Code.OK, case1)
    status5 = Status(Code.OK, case1)
    assert status4 == status5

    # Test inequality of Status with different cases
    case2 = ErrorCase("different_case", Code.ILLEGAL_INPUT)
    status6 = Status(Code.OK, case2)
    assert status4 != status6

    # Test inequality of Status with and without case
    assert status1 != status4

    # Test comparison with non-Status objects
    assert status1 != "not a status"
    assert status1 != 123
    assert status1 != None


def test_status_simple_str():
    status = Status(Code.OK, message="Operation successful")
    assert status.simple_str() == "(code=OK(0), message='Operation successful')"


def test_status_str_representation():
    # Test string representation of Status
    status = Status(Code.OK, message="Operation successful")
    print(status)
    assert str(status) == "(code=OK(0), message='Operation successful')"

    # Test string representation with empty message
    status = Status(Code.ILLEGAL_INPUT)
    assert str(status) == "(code=ILLEGAL_INPUT(3))"

    # Test string representation with case
    case = ErrorCase("test_case", Code.PERMISSION_DENIED)
    status = Status(Code.PERMISSION_DENIED, case, "Access denied")
    assert (
        str(status)
        == "(code=PERMISSION_DENIED(7), case=test_case, message='Access denied')"
    )

    # Test string representation with details
    details = {"reason": "Invalid input"}
    status = Status(Code.ILLEGAL_INPUT, message="Invalid input", details=details)
    assert (
        str(status)
        == "(code=ILLEGAL_INPUT(3), message='Invalid input', details={'reason': 'Invalid input'})"
    )

    # Test with empty details
    status = Status(Code.OK, message="Success", details={})
    assert str(status) == "(code=OK(0), message='Success', details={})"

    # Test with None details
    status = Status(Code.INTERNAL_ERROR, message="Internal error", details=None)
    assert str(status) == "(code=INTERNAL_ERROR(13), message='Internal error')"


def test_status_pseduo_enum_code():
    assert STATUS_OK._code == Code.OK
    assert STATUS_OP_CANCELLED._code == Code.OP_CANCELLED
    assert STATUS_UNKNOWN_ERROR._code == Code.UNKNOWN_ERROR
    assert STATUS_ILLEGAL_INPUT._code == Code.ILLEGAL_INPUT
    assert STATUS_TIMEOUT._code == Code.TIMEOUT
    assert STATUS_NOT_FOUND._code == Code.NOT_FOUND
    assert STATUS_ALREADY_EXISTS._code == Code.ALREADY_EXISTS
    assert STATUS_PERMISSION_DENIED._code == Code.PERMISSION_DENIED
    assert STATUS_UNAUTHENTICATED._code == Code.UNAUTHENTICATED
    assert STATUS_RESOURCE_EXHAUSTED._code == Code.RESOURCE_EXHAUSTED
    assert STATUS_FAILED_PRECONDITION._code == Code.FAILED_PRECONDITION
    assert STATUS_OP_ABORTED._code == Code.OP_ABORTED
    assert STATUS_OUT_OF_RANGE._code == Code.OUT_OF_RANGE
    assert STATUS_UNIMPLEMENTED._code == Code.UNIMPLEMENTED
    assert STATUS_INTERNAL_ERROR._code == Code.INTERNAL_ERROR
    assert STATUS_UNAVAILABLE._code == Code.UNAVAILABLE
    assert STATUS_ILLEGAL_STATE._code == Code.ILLEGAL_STATE
    assert STATUS_AUTHORIZATION_EXPIRED._code == Code.AUTHORIZATION_EXPIRED


def test_new_from_http_resp():
    # 测试有效的 HTTP 状态码
    status = Status.new_from_http_resp(200)
    assert status._code == Code.OK
    assert status._details is None

    status = Status.new_from_http_resp(404)
    assert status._code == Code.NOT_FOUND
    assert status._details is None

    status = Status.new_from_http_resp(403)
    assert status._code == Code.PERMISSION_DENIED
    assert status._details is None

    # 测试带响应头和响应体的状态码
    headers = {"Content-Type": "application/json"}
    body = '{"error": "Not Found"}'
    status = Status.new_from_http_resp(
        404, Response(status_code=404, headers=headers, body=body)
    )
    assert status._code == Code.NOT_FOUND
    assert status._details == {
        "resp": Response(status_code=404, headers=headers, body=body)
    }

    # 测试无效的 HTTP 状态码
    status = Status.new_from_http_resp(999)
    assert status._code == Code.UNKNOWN_ERROR
    assert status._details is None

    # 测试边界值
    status = Status.new_from_http_resp(0)
    assert status._code == Code.UNKNOWN_ERROR
    assert status._details is None

    status = Status.new_from_http_resp(-1)
    assert status._code == Code.UNKNOWN_ERROR
    assert status._details is None
