import sys

import pytest

from src.utils.text_formatter import format_hebrew, is_hebrew


def test_is_hebrew():
    """Test Hebrew character detection."""
    assert is_hebrew("שלום")
    assert is_hebrew("חיים 123")
    assert not is_hebrew("hello")
    assert not is_hebrew("123")
    assert is_hebrew("hello שלום")  # Mixed text


@pytest.mark.parametrize("input_text,expected", [
    ("חיים וייצמן", "ןמצייו םייח"),
    ("בן גוריון", "ןוירוג ןב"),
    ("רחובות", "תובוחר"),
])
def test_hebrew_only_text(input_text, expected):
    """Test formatting of pure Hebrew text."""
    assert format_hebrew(input_text) == expected


@pytest.mark.parametrize("input_text,expected", [
    ("חיים וייצמן 25", "25 ןמצייו םייח"),
    ("הרצל 12", "12 לצרה"),
    ("רחובות 123", "123 תובוחר"),
])
def test_hebrew_with_numbers(input_text, expected):
    """Test formatting of Hebrew text with numbers."""
    assert format_hebrew(input_text) == expected


@pytest.mark.parametrize("input_text,expected", [
    ("hello world", "hello world"),
    ("test 123", "test 123"),
    ("abc def", "abc def"),
])
def test_non_hebrew_text(input_text, expected):
    """Test that non-Hebrew text remains unchanged."""
    assert format_hebrew(input_text) == expected


@pytest.mark.parametrize("input_text,expected", [
    ("שלום hello", "hello םולש"),
    ("hello שלום", "םולש hello"),
    ("שלום hello 123", "123 hello םולש"),
])
def test_mixed_text(input_text, expected):
    """Test formatting of mixed Hebrew and English text."""
    assert format_hebrew(input_text) == expected


@pytest.mark.parametrize("input_text,expected", [
    ("", ""),
    ("   ", ""),
    ("123", "123"),
    ("12 34 56", "12 34 56"),
])
def test_special_cases(input_text, expected):
    """Test edge cases and special inputs."""
    assert format_hebrew(input_text) == expected


def test_exe_environment():
    """Test behavior in exe environment."""
    original_frozen = getattr(sys, 'frozen', False)
    test_text = "חיים וייצמן 25"
    
    try:
        # Simulate exe environment
        sys.frozen = True
        assert format_hebrew(test_text) == test_text, "Text should remain unchanged in exe environment"
        
    finally:
        # Restore original state
        if original_frozen:
            sys.frozen = True
        else:
            delattr(sys, 'frozen') if hasattr(sys, 'frozen') else None