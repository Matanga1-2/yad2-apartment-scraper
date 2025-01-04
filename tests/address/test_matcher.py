import json
import logging

import pytest

from src.address import AddressMatcher
from src.utils.logging_config import setup_logging

# Use the centralized logging configuration
setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def matcher(tmp_path):
    # Create a temporary test data file with multiple cities
    test_data = [
        {
            "city": "Test City",
            "neighborhoods": [
                {
                    "neighborhood": "Test Neighborhood",
                    "streets": [
                        {"name": "אברמוביץ"},
                        {"name": "ביתר", "constraint": "זוגיים בלבד"},
                        {"name": "צבי הירש קלישר"}
                    ]
                }
            ]
        },
        {
            "city": "Other City",
            "neighborhoods": [
                {
                    "neighborhood": "Other Neighborhood",
                    "streets": [
                        {"name": "אברמוביץ"},  # Same street name, different city
                        {"name": "רחוב אחר"}
                    ]
                }
            ]
        }
    ]
    
    json_file = tmp_path / "test_streets.json"
    json_file.write_text(json.dumps(test_data), encoding='utf-8')
    
    # Print the test data for debugging
    print("\nTest data written to file:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    matcher = AddressMatcher(str(json_file))
    
    # Print the loaded lookup dictionary
    print("\nLoaded street lookup:")
    print(json.dumps(matcher.street_lookup, indent=2, ensure_ascii=False))
    
    return matcher

def test_exact_match(matcher):
    result = matcher.is_street_allowed("אברמוביץ", "Test City")
    assert result.is_allowed
    assert result.neighborhood == "Test Neighborhood"
    assert result.city == "Test City"
    assert result.constraint is None

def test_match_with_constraint(matcher):
    result = matcher.is_street_allowed("ביתר", "Test City")
    assert result.is_allowed
    assert result.constraint == "זוגיים בלבד"
    assert result.city == "Test City"

def test_no_match(matcher):
    result = matcher.is_street_allowed("רחוב לא קיים", "Test City")
    assert not result.is_allowed
    assert result.neighborhood is None
    assert result.city is None
    assert result.constraint is None

def test_fuzzy_match(matcher):
    result = matcher.is_street_allowed("אברמוביץ'", "Test City")
    assert result.is_allowed
    assert result.neighborhood == "Test Neighborhood"
    assert result.city == "Test City"

def test_street_with_number(matcher):
    result = matcher.is_street_allowed("צבי הירש קלישר 65", "Test City")
    assert result.is_allowed
    assert result.neighborhood == "Test Neighborhood"
    assert result.city == "Test City"
    assert result.constraint is None

def test_same_street_different_city(matcher):
    # Should match in Test City
    result1 = matcher.is_street_allowed("אברמוביץ", "Test City")
    assert result1.is_allowed
    assert result1.city == "Test City"
    assert result1.neighborhood == "Test Neighborhood"

    # Should match in Other City
    result2 = matcher.is_street_allowed("אברמוביץ", "Other City")
    assert result2.is_allowed
    assert result2.city == "Other City"
    assert result2.neighborhood == "Other Neighborhood"

    # Should not match in Non-existent City
    result3 = matcher.is_street_allowed("אברמוביץ", "Non-existent City")
    assert not result3.is_allowed