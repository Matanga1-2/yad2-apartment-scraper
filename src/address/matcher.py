import json
import logging
from dataclasses import dataclass
from typing import Optional

from fuzzywuzzy import fuzz


@dataclass
class StreetMatch:
    is_allowed: bool
    constraint: Optional[str] = None
    neighborhood: Optional[str] = None

class AddressMatcher:
    def __init__(self, json_file_path: str):
        """Initialize the AddressMatcher with a JSON file containing allowed streets."""
        self.logger = logging.getLogger(__name__)
        self._load_streets(json_file_path)

    def _load_streets(self, json_file_path: str) -> None:
        """Load and parse the streets JSON file."""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                self.cities_data = json.load(f)
            
            # Create a flat lookup dictionary for faster searching
            self.street_lookup = {}
            for city in self.cities_data:
                for neighborhood in city['neighborhoods']:
                    for street in neighborhood['streets']:
                        key = self._normalize_street_name(street['name'])
                        self.street_lookup[key] = {
                            'name': street['name'],
                            'constraint': street.get('constraint'),
                            'neighborhood': neighborhood['neighborhood'],
                            'city': city['city']
                        }
        except Exception as e:
            self.logger.error(f"Failed to load streets file: {e}")
            raise

    def _normalize_street_name(self, street_name: str) -> str:
        """Normalize a street name for comparison."""
        # Remove quotes and special characters
        normalized = street_name.replace('"', '').replace('\'', '')
        # Remove Hebrew abbreviation marks
        normalized = normalized.replace('\"', '').replace('"', '')
        return normalized.strip()

    def _find_best_match(self, street_name: str) -> Optional[dict]:
        """Find the best matching street using fuzzy matching."""
        normalized_input = self._normalize_street_name(street_name)
        best_ratio = 0
        best_match = None

        for lookup_name, street_data in self.street_lookup.items():
            # Try exact match first
            if normalized_input == lookup_name:
                return street_data

            # Try fuzzy match
            ratio = fuzz.ratio(normalized_input, lookup_name)
            if ratio > best_ratio and ratio >= 85:  # Threshold of 85%
                best_ratio = ratio
                best_match = street_data

        return best_match

    def is_street_allowed(self, street_name: str) -> StreetMatch:
        """
        Check if a street is in the allowed list.
        
        Args:
            street_name: The name of the street to check

        Returns:
            StreetMatch object containing:
            - is_allowed: Boolean indicating if the street is allowed
            - constraint: Optional string with any constraints on the street
            - neighborhood: The neighborhood name if the street is found
        """
        # Extract just the street name if address includes number
        street_name = street_name.split()[0]

        match = self._find_best_match(street_name)
        if not match:
            self.logger.debug(f"Street not found: {street_name}")
            return StreetMatch(is_allowed=False)

        self.logger.debug(
            f"Street '{street_name}' matched to '{match['name']}' "
            f"in {match['neighborhood']}, {match['city']}"
        )

        return StreetMatch(
            is_allowed=True,
            constraint=match.get('constraint'),
            neighborhood=match['neighborhood']
        ) 