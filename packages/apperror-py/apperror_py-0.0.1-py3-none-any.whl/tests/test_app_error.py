import traceback

from apperror.app_error import AppError, ErrorBuilder, IllegalArgError
from apperror.op_status import Code
from tests.test_op_status import ErrorCase


class Connection:
    def exec_sql(self, sql: str):
        raise RuntimeError("Network error")


class DBClient:
    def __init__(self, conn: Connection):
        self._conn = conn

    def insert(self, data: str):
        try:
            self._conn.exec_sql("insert into ...")
        except RuntimeError as e:
            raise (
                ErrorBuilder.new_internal_error()
                .with_message("DB insert failed")
                .build(AppError)
            ) from e


class Service:
    def __init__(self, db: DBClient):
        self._db = db

    def save(self, data: str):
        self._db.insert(data)


class API:
    def __init__(self, service: Service):
        self._service = service

    def create(self, data: str):
        self._service.save(data)


def test_app_error_print_stack():
    api = API(Service(DBClient(Connection())))
    try:
        api.create("test")
    except AppError:
        # print(f"error info: {e}")
        print(traceback.format_exc())


def test_check_app_error_cause():
    try:
        api = API(Service(DBClient(Connection())))
        api.create("test")
    except AppError as e:
        assert e.__cause__ is not None
        assert isinstance(e.__cause__, RuntimeError)
        assert e.__cause__.args[0] == "Network error"
        assert e.__context__ is not None
        assert isinstance(e.__context__, RuntimeError)
        assert e.__context__.args[0] == "Network error"


def test_build_app_error():
    e = ErrorBuilder.new_internal_error().with_message("internal error").build()
    assert isinstance(e, AppError)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "internal error"

    class MyAppError(AppError):
        pass

    e = (
        ErrorBuilder.new_internal_error()
        .with_message("internal error")
        .build(MyAppError)
    )
    assert isinstance(e, MyAppError)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "internal error"


def test_app_error_module_property():
    e = ErrorBuilder.new_internal_error().with_module("test_module").build()
    assert isinstance(e, AppError)
    assert e.module == "test_module"
    assert e.status.code == Code.INTERNAL_ERROR

    # 测试空模块名
    e = ErrorBuilder.new_internal_error().with_module("").build()
    assert e.module == "none"

    # 测试空白字符模块名
    e = ErrorBuilder.new_internal_error().with_module("   ").build()
    assert e.module == "none"


def test_app_error_str():
    # 测试基本错误信息
    e = ErrorBuilder.new_internal_error().with_message("internal error").build()
    assert (
        str(e)
        == "AppError(module=none, status=(code=INTERNAL_ERROR(13), message='internal error'))"
    )

    # 测试带模块名的错误信息
    e = (
        ErrorBuilder.new_internal_error()
        .with_module("test_module")
        .with_message("internal error")
        .build()
    )
    assert (
        str(e)
        == "AppError(module=test_module, status=(code=INTERNAL_ERROR(13), message='internal error'))"
    )

    # 测试带 case 的错误信息
    e = (
        ErrorBuilder.new_internal_error()
        .with_case(ErrorCase("1001", Code.INTERNAL_ERROR))
        .with_message("internal error")
        .build()
    )
    assert (
        str(e)
        == "AppError(module=none, status=(code=INTERNAL_ERROR(13), case=1001, message='internal error'))"
    )

    # 测试带 details 的错误信息
    e = (
        ErrorBuilder.new_internal_error()
        .with_details({"key": "value"})
        .with_message("internal error")
        .build()
    )
    assert (
        str(e)
        == "AppError(module=none, status=(code=INTERNAL_ERROR(13), message='internal error', details={'key': 'value'}))"
    )

    # 测试完整错误信息
    e = (
        ErrorBuilder.new_internal_error()
        .with_module("test_module")
        .with_case(ErrorCase("1001", Code.INTERNAL_ERROR))
        .with_details({"key": "value"})
        .with_message("internal error")
        .build()
    )
    assert (
        str(e)
        == "AppError(module=test_module, status=(code=INTERNAL_ERROR(13), case=1001, message='internal error', details={'key': 'value'}))"
    )


def test_build_error_with_kwargs():
    # 测试不传入关键字参数
    e = ErrorBuilder.new_internal_error().with_message("internal error").build()
    assert isinstance(e, AppError)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "internal error"
    assert e.status.details is None

    # 测试传入关键字参数
    e = (
        ErrorBuilder.new_internal_error()
        .with_message("internal error")
        .build(key1="value1")
    )
    assert isinstance(e, AppError)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "internal error"
    assert e.status.details == {"key1": "value1"}

    # 测试传入多个关键字参数
    e = (
        ErrorBuilder.new_internal_error()
        .with_message("internal error")
        .build(key1="value1", extra_info={"key2": "value2"})
    )
    assert isinstance(e, AppError)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "internal error"
    assert e.status.details == {"key1": "value1", "extra_info": {"key2": "value2"}}


# Test AppError.new_illegal_arg method
def test_new_illegal_arg():
    # Test basic illegal argument error creation
    e = AppError.new_illegal_arg("illegal arg")
    assert isinstance(e, IllegalArgError)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "illegal arg"
    assert e.module == "none"

    # Test illegal argument error with custom module
    e = AppError.new_illegal_arg("illegal arg", module="validation")
    assert isinstance(e, IllegalArgError)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "illegal arg"
    assert e.module == "validation"

    # Test illegal argument error with empty module
    e = AppError.new_illegal_arg("illegal data", module="")
    assert isinstance(e, IllegalArgError)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "illegal data"
    assert e.module == "none"

    # Test illegal argument error with whitespace module
    e = AppError.new_illegal_arg("illegal format", module="   ")
    assert isinstance(e, IllegalArgError)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "illegal format"
    assert e.module == "none"

    # Test string representation
    e = AppError.new_illegal_arg("Test error", module="test_module")
    assert (
        str(e)
        == "IllegalArgError(module=test_module, status=(code=INTERNAL_ERROR(13), message='Test error'))"
    )
