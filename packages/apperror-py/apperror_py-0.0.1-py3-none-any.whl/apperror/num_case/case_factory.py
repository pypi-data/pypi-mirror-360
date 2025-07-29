import math

from apperror.num_case.code_mapper import CodeMapper
from apperror.num_case.num_case import NumCase
from apperror.num_case.num_range import NumRange
from apperror.op_status import Code
from apperror.utils import check_arg


class CaseFactory:
    """
    CaseFactory creates NumCase instances with proper case IDs.
    """

    def __init__(
        self,
        num_digits_for_app_code: int,
        num_digits_for_module_code: int,
        num_digits_for_case_code: int,
        code_mapper: CodeMapper,
        app_code: int = 0,
        module_code: int = 0,
    ):
        """
        Initialize a CaseFactory.

        Args:
            num_digits_for_app_code: Number of digits for app code
            num_digits_for_module_code: Number of digits for module code
            num_digits_for_case_code: Number of digits for case code
            code_mapper: Mapper mapping operation status codes to case code segments
            app_code: a numerical code for an whole application
            module_code: a numerical code for a module in the application
        """

        check_arg(num_digits_for_app_code >= 0, "num_digits_for_app_code < 0")
        check_arg(num_digits_for_module_code >= 0, "num_digits_for_module_code < 0")
        check_arg(num_digits_for_case_code >= 0, "num_digits_for_case_code < 0")
        check_arg(code_mapper is not None, "code_mapper is None")
        check_arg(app_code >= 0, "app_code < 0")
        check_arg(module_code >= 0, "module_code < 0")

        self.num_digits_for_app_code = num_digits_for_app_code
        self.num_digits_for_module_code = num_digits_for_module_code
        self.num_digits_for_case_code = num_digits_for_case_code
        self.code_mapper = code_mapper
        self.app_code = app_code
        self.module_code = module_code
        self.app_code_range = NumRange(
            0, int(math.pow(10, num_digits_for_app_code)) - 1
        )
        self.module_code_range = NumRange(
            0, int(math.pow(10, num_digits_for_module_code)) - 1
        )
        self.case_code_range = NumRange(
            0, int(math.pow(10, num_digits_for_case_code)) - 1
        )

        check_arg(
            self.app_code_range.include(app_code),
            f"app_code_range {self.app_code_range} not include given app_code {app_code}",
        )
        check_arg(
            self.module_code_range.include(module_code),
            f"module_code_range {self.module_code_range} not include given module_code {module_code}",
        )

        # Validate case code segments
        segs = code_mapper.case_code_segments()
        segs.sort(key=lambda x: x.end)
        for cs in segs:
            check_arg(
                self.case_code_range.include_range(cs),
                f"this.case_code_range {self.case_code_range} doesn't include "
                f"CaseCodeSegment {cs} defined by this.code_mapper",
            )

    def _create(self, status_code: Code, case_code: int) -> NumCase:
        """
        Create a NumCase with the given status code and case code.

        Args:
            status_code: Status code
            case_code: Case code

        Returns:
            Created NumCase

        Raises:
            ValueError: If case code is invalid
        """
        code_seg = self.code_mapper.case_code_segment_for(status_code)
        # check_arg(
        #     code_seg is not None,
        #     f"status_code_mapper doesn't define a CaseCodeSegment for status code {status_code}"
        # )
        if code_seg is None:
            raise ValueError(
                f"code_mapper doesn't define a CaseCodeSegment for given status_code {status_code}"
            )
        check_arg(
            code_seg.include(case_code),
            f"CaseCodeSegment {code_seg} for given status_code {status_code} doesn't include given case_code {case_code}",
        )
        return NumCase(
            app_code=self.app_code,
            module_code=self.module_code,
            case_code=case_code,
            identifier=self.build_case_id(case_code),
        )

    def _pad_left_zeros(self, num: int, min_len: int) -> str:
        """
        Pad given number with leading zeros to reach minimum length.

        Args:
            num: Number to pad
            min_len: Minimum length

        Returns:
            Padded string
        """
        s = str(num)
        if len(s) >= min_len:
            return s
        return "0" * (min_len - len(s)) + s

    def build_case_id(self, case_code: int) -> str:
        id_parts = []
        if self.num_digits_for_app_code > 0:
            id_parts.append(
                self._pad_left_zeros(self.app_code, self.num_digits_for_app_code)
            )
        if self.num_digits_for_module_code > 0:
            id_parts.append(
                self._pad_left_zeros(self.module_code, self.num_digits_for_module_code)
            )
        id_parts.append(self._pad_left_zeros(case_code, self.num_digits_for_case_code))
        return "_".join(id_parts)

    def new_illegal_input(self, case_code: int) -> NumCase:
        return self._create(Code.ILLEGAL_INPUT, case_code)

    def new_timeout(self, case_code: int) -> NumCase:
        return self._create(Code.TIMEOUT, case_code)

    def new_not_found(self, case_code: int) -> NumCase:
        return self._create(Code.NOT_FOUND, case_code)

    def new_already_exists(self, case_code: int) -> NumCase:
        return self._create(Code.ALREADY_EXISTS, case_code)

    def new_permission_denied(self, case_code: int) -> NumCase:
        return self._create(Code.PERMISSION_DENIED, case_code)

    def new_resource_exhausted(self, case_code: int) -> NumCase:
        return self._create(Code.RESOURCE_EXHAUSTED, case_code)

    def new_failed_precondition(self, case_code: int) -> NumCase:
        return self._create(Code.FAILED_PRECONDITION, case_code)

    def new_op_aborted(self, case_code: int) -> NumCase:
        return self._create(Code.OP_ABORTED, case_code)

    def new_out_of_range(self, case_code: int) -> NumCase:
        return self._create(Code.OUT_OF_RANGE, case_code)

    def new_internal_error(self, case_code: int) -> NumCase:
        return self._create(Code.INTERNAL_ERROR, case_code)

    def new_illegal_state(self, case_code: int) -> NumCase:
        return self._create(Code.ILLEGAL_STATE, case_code)
