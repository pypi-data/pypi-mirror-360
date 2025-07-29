from apperror.num_case.code_mapper import DefaultCodeMapper
from apperror.num_case.num_range import NumRange
from apperror.op_status import Code


def test_has_mapping_for():
    """Test checking if a status code has a mapping"""
    cm = DefaultCodeMapper()
    # Test codes that should have mappings
    assert cm.has_mapping_for(Code.ILLEGAL_INPUT)
    assert cm.has_mapping_for(Code.TIMEOUT)
    assert cm.has_mapping_for(Code.NOT_FOUND)

    # Test codes that should not have mappings
    assert not cm.has_mapping_for(Code.OK)
    assert not cm.has_mapping_for(Code.OP_CANCELLED)
    assert not cm.has_mapping_for(Code.UNKNOWN_ERROR)


def test_case_code_segment_for():
    """Test getting case code segment for a status code"""
    cm = DefaultCodeMapper()

    # Test valid mappings
    assert cm.case_code_segment_for(Code.ILLEGAL_INPUT) == NumRange(1, 50)
    assert cm.case_code_segment_for(Code.TIMEOUT) == NumRange(51, 100)
    assert cm.case_code_segment_for(Code.NOT_FOUND) == NumRange(101, 150)

    # Test codes without mappings
    assert cm.case_code_segment_for(Code.OK) is None
    assert cm.case_code_segment_for(Code.OP_CANCELLED) is None


def test_case_code_segments():
    """Test getting all case code segments"""
    cm = DefaultCodeMapper()
    segments = cm.case_code_segments()

    # Check that we have the expected number of segments
    assert len(segments) == 11

    # Check that all segments are NumRange instances
    assert all(isinstance(seg, NumRange) for seg in segments)

    # Check that segments don't overlap
    for i, seg1 in enumerate(segments):
        for seg2 in segments[i + 1 :]:
            assert not seg1.overlap(seg2)


def test_mappings():
    """Test getting all mappings"""
    cm = DefaultCodeMapper()
    mappings = cm.mappings()

    # Check that we have the expected number of mappings
    assert len(mappings) == 11

    # Check that all values are NumRange instances
    assert all(isinstance(seg, NumRange) for seg in mappings.values())

    assert mappings[Code.ILLEGAL_INPUT] == NumRange(1, 50)
    assert mappings[Code.TIMEOUT] == NumRange(51, 100)
    assert mappings[Code.NOT_FOUND] == NumRange(101, 150)
    assert mappings[Code.ALREADY_EXISTS] == NumRange(151, 200)
    assert mappings[Code.PERMISSION_DENIED] == NumRange(201, 250)
    assert mappings[Code.RESOURCE_EXHAUSTED] == NumRange(251, 300)
    assert mappings[Code.FAILED_PRECONDITION] == NumRange(301, 350)
    assert mappings[Code.OP_ABORTED] == NumRange(351, 400)
    assert mappings[Code.OUT_OF_RANGE] == NumRange(401, 450)
    assert mappings[Code.INTERNAL_ERROR] == NumRange(451, 500)
    assert mappings[Code.ILLEGAL_STATE] == NumRange(501, 550)


def test_str_representation():
    cm = DefaultCodeMapper()
    print(cm)
