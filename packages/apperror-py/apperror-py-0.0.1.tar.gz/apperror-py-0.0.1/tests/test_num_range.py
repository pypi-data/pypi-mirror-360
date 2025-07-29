import pytest

from apperror.num_case.num_range import NumRange


def test_init_valid_range():
    """Test initializing NumRange with valid arguments"""
    range1 = NumRange(0, 5)
    assert range1.start == 0
    assert range1.end == 5

    range2 = NumRange(10, 10)
    assert range2.start == 10
    assert range2.end == 10


def test_init_invalid_range():
    """Test initializing NumRange with invalid arguments"""
    with pytest.raises(ValueError, match="start < 0"):
        NumRange(-1, 5)

    with pytest.raises(ValueError, match="end < 0"):
        NumRange(0, -1)

    with pytest.raises(ValueError, match="end < start"):
        NumRange(10, 5)


def test_include():
    """Test include method"""
    range1 = NumRange(0, 5)
    assert range1.include(0) == True
    assert range1.include(3) == True
    assert range1.include(5) == True
    assert range1.include(-1) == False
    assert range1.include(6) == False


def test_include_range():
    """Test include_range method"""
    range1 = NumRange(0, 10)
    range2 = NumRange(2, 8)
    range3 = NumRange(5, 15)

    assert range1.include_range(range2) == True
    assert range1.include_range(range3) == False
    assert range1.include_range(range1) == True


def test_str():
    """Test string representation"""
    range1 = NumRange(0, 5)
    assert str(range1) == "[0, 5]"


def test_repr():
    """Test detailed string representation"""
    range1 = NumRange(0, 5)
    assert repr(range1) == "NumRange(start=0, end=5)"
