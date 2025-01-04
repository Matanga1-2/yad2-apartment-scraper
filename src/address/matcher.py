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
    city: Optional[str] = None

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
            for city_data in self.cities_data:
                city_name = city_data['city']
                for neighborhood in city_data['neighborhoods']:
                    neighborhood_name = neighborhood['neighborhood']
                    for street in neighborhood['streets']:
                        street_name = street['name']
                        normalized_street = self._normalize_street_name(street_name)
                        normalized_city = self._normalize_text(city_name)
                        # Create a composite key of city and street
                        key = f"{normalized_city}:{normalized_street}"
                        
                        self.street_lookup[key] = {
                            'name': street_name,
                            'constraint': street.get('constraint'),
                            'neighborhood': neighborhood_name,
                            'city': city_name
                        }
        except Exception as e:
            self.logger.error(f"Failed to load streets file: {e}")
            raise

    def _normalize_text(self, text: str) -> str:
        """Normalize any text for comparison."""
        # Remove quotes and special characters
        normalized = text.replace('"', '').replace('\'', '')
        # Remove Hebrew abbreviation marks
        normalized = normalized.replace('\"', '').replace('"', '')
        return normalized.strip()  # Remove just whitespace, no lower() for Hebrew

    def _normalize_street_name(self, street_name: str) -> str:
        """Normalize a street name for comparison."""
        return self._normalize_text(street_name)

    def _find_best_match(self, street_name: str, city: str) -> Optional[dict]:
        """Find the best matching street using fuzzy matching within the specified city."""
        normalized_input = self._normalize_street_name(street_name)
        normalized_city = self._normalize_text(city)
        
        # Create the composite key for exact match
        exact_key = f"{normalized_city}:{normalized_input}"
        
        # Try exact match first
        if exact_key in self.street_lookup:
            return self.street_lookup[exact_key]

        # If no exact match, try fuzzy matching
        best_ratio = 0
        best_match = None

        # Filter potential matches by city first
        city_keys = [k for k in self.street_lookup.keys() if k.startswith(f"{normalized_city}:")]
        
        for key in city_keys:
            _, street_part = key.split(":", 1)
            ratio = fuzz.ratio(normalized_input, street_part)
            if ratio > best_ratio and ratio >= 85:
                best_ratio = ratio
                best_match = self.street_lookup[key]

        return best_match

    def is_street_allowed(self, street_name: str, city: str) -> StreetMatch:
        """
        Check if a street is in the allowed list for the specified city.
        
        Args:
            street_name: The name of the street to check
            city: The city to check the street in

        Returns:
            StreetMatch object containing:
            - is_allowed: Boolean indicating if the street is allowed
            - constraint: Optional string with any constraints on the street
            - neighborhood: The neighborhood name if the street is found
            - city: The city name if the street is found
        """
        # Extract just the street name if address includes number
        parts = street_name.split()
        for i in range(len(parts)-1, -1, -1):
            if not parts[i].isdigit():
                street_name = ' '.join(parts[:i+1])
                break

        match = self._find_best_match(street_name, city)
        if not match:
            self.logger.debug(f"Street not found: {street_name} in city: {city}")
            return StreetMatch(is_allowed=False)

        return StreetMatch(
            is_allowed=True,
            constraint=match.get('constraint'),
            neighborhood=match['neighborhood'],
            city=match['city']
        ) 