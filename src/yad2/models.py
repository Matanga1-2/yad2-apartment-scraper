from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PropertyFeatures:
    has_elevator: bool = False
    has_parking: bool = False
    has_mamad: bool = False  # ממ"ד
    has_balcony: bool = False
    has_storage: bool = False
    total_floors: Optional[int] = None
    current_floor: Optional[int] = None

@dataclass
class Contact:
    name: Optional[str]
    phone: Optional[str]

@dataclass
class PropertySpecs:
    rooms: Optional[float] = None
    floor: Optional[int] = None
    size_sqm: Optional[int] = None
    features: PropertyFeatures = field(default_factory=PropertyFeatures)

@dataclass
class Location:
    city: str
    street: str
    neighborhood: Optional[str] = None
    area: Optional[str] = None

@dataclass
class FeedItem:
    item_id: str
    url: str
    price: Optional[int]
    location: Location
    specs: PropertySpecs
    is_saved: bool
    is_agency: bool
    agency_name: Optional[str] = None
    contact: Optional[Contact] = None
    tags: List[str] = field(default_factory=list)

    def format_listing(self) -> str:
        """
        Formats the listing in the standard Hebrew format:
        {Street}, {Neighborhood}, {City}, {Number of Rooms} חד', 
        קומה {Current Floor}/{Total Floors}, {Features}, {Price in thousands} - {Listing Type} - {Contact}
        """
        main_parts = []
        end_parts = []
        
        # Location
        location_parts = [self.location.street]
        if self.location.neighborhood:
            location_parts.append(self.location.neighborhood)
        location_parts.append(self.location.city)
        main_parts.append(", ".join(location_parts))

        # Rooms
        if self.specs.rooms:
            # Format rooms as integer if it's a whole number, otherwise keep decimal
            rooms_str = str(int(self.specs.rooms)) if self.specs.rooms.is_integer() else str(self.specs.rooms)
            main_parts.append(f"{rooms_str} חד׳")
            
        # Floor
        if self.specs.features.current_floor and self.specs.features.total_floors:
            main_parts.append(f"קומה {self.specs.features.current_floor}/{self.specs.features.total_floors}")
        
        # Features
        features = []
        if self.specs.features.has_elevator:
            features.append("מעלית")
        if self.specs.features.has_parking:
            features.append("חניה")
        if self.specs.features.has_mamad:
            features.append("ממ״ד")
        if self.specs.features.has_storage:
            features.append("מחסן")
        if self.specs.features.has_balcony:
            features.append("מרפסת")
        if features:
            main_parts.extend(features)
        
        # Price (in thousands)
        if self.price:
            price_thousands = self.price // 1000
            main_parts.append(str(price_thousands))
        
        # Listing type (goes to end_parts)
        listing_type = "מתיווך" if self.is_agency else "פרטי"
        end_parts.append(listing_type)
        
        # Contact (goes to end_parts)
        if self.contact:
            contact_str = f"{self.contact.name} {self.contact.phone}" if self.contact.name else self.contact.phone
            end_parts.append(contact_str)
        
        # Join main parts with commas, then join with end parts using dashes
        return f"{', '.join(main_parts)} - {' - '.join(end_parts)}"
