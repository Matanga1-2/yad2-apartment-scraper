import json
import logging
import pytest
from src.address import AddressMatcher, StreetMatch

# Setup logger at module level
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Only add handler if none exists to prevent duplicate handlers
if not logger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(name)s - %(message)s')
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
@pytest.fixture
def matcher(tmp_path):
    # Create a temporary test data file
    test_data = [
        {
            "city": "Test City",
            "neighborhoods": [
                {
                    "neighborhood": "Test Neighborhood",
                    "streets": [
                        {"name": "אברמוביץ"},
                        {"name": "ביתר", "constraint": "זוגיים בלבד"}
                    ]
                }
            ]
        }
    ]
    
    json_file = tmp_path / "test_streets.json"
    json_file.write_text(json.dumps(test_data), encoding='utf-8')
    return AddressMatcher(str(json_file))

def test_exact_match(matcher):
    result = matcher.is_street_allowed("אברמוביץ")
    logger.info(f"Tried matching \"אברמוביץ\" with file, result is: {result}")
    assert result.is_allowed
    assert result.neighborhood == "Test Neighborhood"
    assert result.constraint is None

def test_match_with_constraint(matcher):
    result = matcher.is_street_allowed("ביתר")
    logger.info(f"Tried matching \"ביתר\" with file, result is: {result}")
    assert result.is_allowed
    assert result.constraint == "זוגיים בלבד"

def test_no_match(matcher):
    result = matcher.is_street_allowed("רחוב לא קיים")
    logger.info(f"Tried matching \"רחוב לא קיים\" with file, result is: {result}")
    assert not result.is_allowed
    assert result.neighborhood is None
    assert result.constraint is None

def test_fuzzy_match(matcher):
    result = matcher.is_street_allowed("אברמוביץ'")
    logger.info(f"Tried matching \"אברמוביץ'\" with file, result is: {result}")
    assert result.is_allowed
    assert result.neighborhood == "Test Neighborhood"