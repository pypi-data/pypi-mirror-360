from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from apperror.num_case.num_range import NumRange
from apperror.op_status import Code, http_status_for

# Type alias for NumRange
CaseCodeSegment = NumRange


class CodeMapper(ABC):
    """Interface for mapping operation status codes to case code segments."""

    @abstractmethod
    def has_mapping_for(self, status_code: Code) -> bool:
        """Check if there is a mapping for the given status code.

        Args:
            status_code: The operation status code to check

        Returns:
            True if there is a mapping, False otherwise
        """
        pass

    @abstractmethod
    def case_code_segment_for(self, status_code: Code) -> Optional[CaseCodeSegment]:
        """Get the case code segment for the given status code.

        Args:
            status_code: The operation status code to look up

        Returns:
            The case code segment if found, None otherwise
        """
        pass

    @abstractmethod
    def case_code_segments(self) -> List[CaseCodeSegment]:
        """Get all case code segments.

        Returns:
            List of all case code segments
        """
        pass

    @abstractmethod
    def mappings(self) -> Dict[Code, CaseCodeSegment]:
        """Get all mappings from status codes to case code segments.

        Returns:
            Dictionary mapping status codes to case code segments
        """
        pass

    @abstractmethod
    def illegal_input(self) -> CaseCodeSegment:
        """Get the case code segment for illegal input errors.

        Returns:
            The case code segment for illegal input errors
        """
        pass

    @abstractmethod
    def timeout(self) -> CaseCodeSegment:
        """Get the case code segment for deadline exceeded errors.

        Returns:
            The case code segment for deadline exceeded errors
        """
        pass

    @abstractmethod
    def not_found(self) -> CaseCodeSegment:
        """Get the case code segment for not found errors.

        Returns:
            The case code segment for not found errors
        """
        pass

    @abstractmethod
    def already_exists(self) -> CaseCodeSegment:
        """Get the case code segment for already exists errors.

        Returns:
            The case code segment for already exists errors
        """
        pass

    @abstractmethod
    def permission_denied(self) -> CaseCodeSegment:
        """Get the case code segment for permission denied errors.

        Returns:
            The case code segment for permission denied errors
        """
        pass

    @abstractmethod
    def resource_exhausted(self) -> CaseCodeSegment:
        """Get the case code segment for resource exhausted errors.

        Returns:
            The case code segment for resource exhausted errors
        """
        pass

    @abstractmethod
    def failed_precondition(self) -> CaseCodeSegment:
        """Get the case code segment for failed precondition errors.

        Returns:
            The case code segment for failed precondition errors
        """
        pass

    @abstractmethod
    def op_aborted(self) -> CaseCodeSegment:
        """Get the case code segment for aborted errors.

        Returns:
            The case code segment for aborted errors
        """
        pass

    @abstractmethod
    def out_of_range(self) -> CaseCodeSegment:
        """Get the case code segment for out of range errors.

        Returns:
            The case code segment for out of range errors
        """
        pass

    @abstractmethod
    def internal_error(self) -> CaseCodeSegment:
        """Get the case code segment for internal errors.

        Returns:
            The case code segment for internal errors
        """
        pass

    @abstractmethod
    def illegal_state(self) -> CaseCodeSegment:
        """Get the case code segment for illegal state errors.

        Returns:
            The case code segment for illegal state errors
        """
        pass


class CodeMapperBase(CodeMapper):
    """Base implementation of CodeMapper."""

    def __init__(self):
        self._status_code_to_case_code_seg: Dict[Code, CaseCodeSegment] = {
            Code.ILLEGAL_INPUT: self.illegal_input(),
            Code.TIMEOUT: self.timeout(),
            Code.NOT_FOUND: self.not_found(),
            Code.ALREADY_EXISTS: self.already_exists(),
            Code.PERMISSION_DENIED: self.permission_denied(),
            Code.RESOURCE_EXHAUSTED: self.resource_exhausted(),
            Code.FAILED_PRECONDITION: self.failed_precondition(),
            Code.OP_ABORTED: self.op_aborted(),
            Code.OUT_OF_RANGE: self.out_of_range(),
            Code.INTERNAL_ERROR: self.internal_error(),
            Code.ILLEGAL_STATE: self.illegal_state(),
        }

    def has_mapping_for(self, status_code: Code) -> bool:
        return status_code in self._status_code_to_case_code_seg

    def case_code_segment_for(self, status_code: Code) -> Optional[CaseCodeSegment]:
        return self._status_code_to_case_code_seg.get(status_code)

    def case_code_segments(self) -> List[CaseCodeSegment]:
        return list(self._status_code_to_case_code_seg.values())

    def mappings(self) -> Dict[Code, CaseCodeSegment]:
        return self._status_code_to_case_code_seg.copy()

    def __str__(self) -> str:
        # Invert the map and sort the segments
        segment_to_op_status_code = {
            segment: status_code
            for status_code, segment in self._status_code_to_case_code_seg.items()
        }
        segments = sorted(segment_to_op_status_code.keys(), key=lambda s: s.end)

        # Build the string
        lines = []
        lines.append("+" + "-" * 88 + "+")
        lines.append(
            "| {:<15} | {:<20}:{:<14} | {:<20}:{:<14} |".format(
                "Case Code Segment", "Operation Status", "Code", "HTTP Status", "Code"
            )
        )
        lines.append("+" + "-" * 88 + "+")

        for segment in segments:
            op_status_code = segment_to_op_status_code[segment]
            http_status = http_status_for(op_status_code)
            if http_status is None:
                raise RuntimeError(f"No HTTP status found for {op_status_code}")
            lines.append(
                "| {:<15} | {:<20}:{:<14} | {:<20}:{:<14} |".format(
                    str(segment),
                    op_status_code.name,
                    str(op_status_code.value),
                    http_status.name,
                    str(http_status.value),
                )
            )
        lines.append("+" + "-" * 88 + "+")

        return "\n".join(lines)


class DefaultCodeMapper(CodeMapperBase):
    def __init__(self):
        super().__init__()

    def illegal_input(self) -> CaseCodeSegment:
        return NumRange(1, 50)

    def timeout(self) -> CaseCodeSegment:
        return NumRange(51, 100)

    def not_found(self) -> CaseCodeSegment:
        return NumRange(101, 150)

    def already_exists(self) -> CaseCodeSegment:
        return NumRange(151, 200)

    def permission_denied(self) -> CaseCodeSegment:
        return NumRange(201, 250)

    def resource_exhausted(self) -> CaseCodeSegment:
        return NumRange(251, 300)

    def failed_precondition(self) -> CaseCodeSegment:
        return NumRange(301, 350)

    def op_aborted(self) -> CaseCodeSegment:
        return NumRange(351, 400)

    def out_of_range(self) -> CaseCodeSegment:
        return NumRange(401, 450)

    def internal_error(self) -> CaseCodeSegment:
        return NumRange(451, 500)

    def illegal_state(self) -> CaseCodeSegment:
        return NumRange(501, 550)
