import pytest

from apperror.http_status import HTTPStatus


def test_http_status():
    # 测试有效的HTTP状态码
    assert HTTPStatus.for_code(200) == HTTPStatus.OK
    assert HTTPStatus.for_code(400) == HTTPStatus.BAD_REQUEST
    assert HTTPStatus.for_code(401) == HTTPStatus.UNAUTHORIZED
    assert HTTPStatus.for_code(403) == HTTPStatus.FORBIDDEN
    assert HTTPStatus.for_code(404) == HTTPStatus.NOT_FOUND
    assert HTTPStatus.for_code(405) == HTTPStatus.METHOD_NOT_ALLOWED
    assert HTTPStatus.for_code(409) == HTTPStatus.CONFLICT
    assert HTTPStatus.for_code(429) == HTTPStatus.TOO_MANY_REQUESTS
    assert HTTPStatus.for_code(499) == HTTPStatus.CLIENT_CLOSED_REQUEST
    assert HTTPStatus.for_code(500) == HTTPStatus.INTERNAL_SERVER_ERROR
    assert HTTPStatus.for_code(501) == HTTPStatus.NOT_IMPLEMENTED
    assert HTTPStatus.for_code(503) == HTTPStatus.SERVICE_UNAVAILABLE
    assert HTTPStatus.for_code(504) == HTTPStatus.TIMEOUT

    # 测试无效的HTTP状态码
    assert HTTPStatus.for_code(100) is None
    assert HTTPStatus.for_code(300) is None
    assert HTTPStatus.for_code(600) is None
    assert HTTPStatus.for_code(-1) is None

    with pytest.raises(ValueError):
        HTTPStatus(-1)


def test_http_status_str_representation():
    assert str(HTTPStatus.OK) == "HTTPStatus.OK(200)"
    assert str(HTTPStatus.BAD_REQUEST) == "HTTPStatus.BAD_REQUEST(400)"
    assert str(HTTPStatus.UNAUTHORIZED) == "HTTPStatus.UNAUTHORIZED(401)"
    assert str(HTTPStatus.FORBIDDEN) == "HTTPStatus.FORBIDDEN(403)"
    assert str(HTTPStatus.NOT_FOUND) == "HTTPStatus.NOT_FOUND(404)"
    assert str(HTTPStatus.METHOD_NOT_ALLOWED) == "HTTPStatus.METHOD_NOT_ALLOWED(405)"
    assert str(HTTPStatus.CONFLICT) == "HTTPStatus.CONFLICT(409)"
    assert str(HTTPStatus.TOO_MANY_REQUESTS) == "HTTPStatus.TOO_MANY_REQUESTS(429)"
