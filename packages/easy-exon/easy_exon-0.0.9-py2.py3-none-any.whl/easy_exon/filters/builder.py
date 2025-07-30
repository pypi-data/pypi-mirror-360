from dataclasses import dataclass, field
from typing import List, Optional
from .enums import City, CityArea, Category, Status


AREA_BY_CITY = {
    City.MOSCOW: [
        CityArea.NORTH_WEST, CityArea.EAST, CityArea.SOUTH,
        CityArea.TROITSKY, CityArea.WEST, CityArea.SOUTH_WEST,
        CityArea.NOVO_MOSCOW, CityArea.NORTH_EAST, CityArea.SOUTH_EAST,
        CityArea.NORTH, CityArea.CENTRAL
    ],
    City.ZELENOGRAD: [
        CityArea.ZELENOGRADSKIY
    ],
}

EMPTY_OBJECT_FILTER = {
    "category":      None,
    "city":          None,
    "cityArea":      None,
    "cityDistricts": None,
    "status":        None,
}


@dataclass
class ObjectFilter:
    category:       List[Category]           = field(default_factory=list)
    city:           City                     = None
    city_area:      Optional[List[CityArea]] = field(default_factory=list)
    city_districts: Optional[List[str]]      = field(default_factory=list)
    status:         List[Status]             = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "category":      [c.value for c in self.category] if self.category else None,
            "city":          self.city.value if self.city else None,
            "cityArea":      [a.value for a in self.city_area] if self.city_area else None,
            "cityDistricts": self.city_districts if self.city_districts else None,
            "status":        [s.value for s in self.status] if self.status else None,
        }
