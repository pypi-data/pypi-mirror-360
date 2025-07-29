import pytest

from apperror.num_case.case_factory import CaseFactory
from apperror.num_case.code_mapper import DefaultCodeMapper
from apperror.num_case.num_case import NumCase


def test_init():
    # 测试正常初始化
    factory = CaseFactory(
        num_digits_for_app_code=2,
        num_digits_for_module_code=2,
        num_digits_for_case_code=3,
        code_mapper=DefaultCodeMapper(),
        app_code=1,
        module_code=2,
    )
    assert factory.app_code == 1
    assert factory.module_code == 2
    assert factory.num_digits_for_app_code == 2
    assert factory.num_digits_for_module_code == 2
    assert factory.num_digits_for_case_code == 3

    # 测试无效参数
    with pytest.raises(ValueError):
        CaseFactory(-1, 2, 3, DefaultCodeMapper())
    with pytest.raises(ValueError):
        CaseFactory(2, -1, 3, DefaultCodeMapper())
    with pytest.raises(ValueError):
        CaseFactory(2, 2, -1, DefaultCodeMapper())
    with pytest.raises(ValueError):
        CaseFactory(2, 2, 3, DefaultCodeMapper(), app_code=-1)
    with pytest.raises(ValueError):
        CaseFactory(2, 2, 3, DefaultCodeMapper(), module_code=-1)


def test_build_case_id():
    factory = CaseFactory(
        num_digits_for_app_code=2,
        num_digits_for_module_code=2,
        num_digits_for_case_code=3,
        code_mapper=DefaultCodeMapper(),
        app_code=1,
        module_code=2,
    )

    # 测试生成case id
    assert factory.build_case_id(123) == "01_02_123"
    assert factory.build_case_id(1) == "01_02_001"

    # 测试不同位数配置
    factory = CaseFactory(
        num_digits_for_app_code=0,
        num_digits_for_module_code=0,
        num_digits_for_case_code=3,
        code_mapper=DefaultCodeMapper(),
    )
    assert factory.build_case_id(123) == "123"


def test_create_cases():
    factory = CaseFactory(
        num_digits_for_app_code=2,
        num_digits_for_module_code=2,
        num_digits_for_case_code=3,
        code_mapper=DefaultCodeMapper(),
        app_code=1,
        module_code=2,
    )

    # 测试创建各种类型的case
    invalid_arg_case = factory.new_illegal_input(1)
    assert isinstance(invalid_arg_case, NumCase)
    assert invalid_arg_case._app_code == 1
    assert invalid_arg_case._module_code == 2
    assert invalid_arg_case._case_code == 1

    not_found_case = factory.new_not_found(101)
    assert isinstance(not_found_case, NumCase)
    assert not_found_case._case_code == 101

    # 测试无效的case code
    with pytest.raises(ValueError):
        factory.new_illegal_input(51)  # 超出InvalidArgument的范围
    with pytest.raises(ValueError):
        factory.new_not_found(1)  # 超出NotFound的范围


def test_pad_left_zeros():
    factory = CaseFactory(
        num_digits_for_app_code=2,
        num_digits_for_module_code=2,
        num_digits_for_case_code=3,
        code_mapper=DefaultCodeMapper(),
    )

    assert factory._pad_left_zeros(1, 3) == "001"
    assert factory._pad_left_zeros(12, 3) == "012"
    assert factory._pad_left_zeros(123, 3) == "123"
    assert factory._pad_left_zeros(1234, 3) == "1234"
