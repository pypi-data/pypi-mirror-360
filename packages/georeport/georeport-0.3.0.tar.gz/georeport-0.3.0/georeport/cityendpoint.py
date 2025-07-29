from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class CityEndpoint:
    """
    Stores the data for a city's endpoint.
    """
    name: str
    root_address: str
    jurisdiction: Optional[str] = None


class CityEndpoints:
    """
    Stores the data for known city endpoints.
    """
    _cities: Dict[str, CityEndpoint] = {
        'Bloomington, IN': CityEndpoint(
            name='Bloomington, IN',
            root_address='https://bloomington.in.gov/crm/open311/v2'
        ),
        'Brookline, MA': CityEndpoint(
            name='Brookline, MA',
            root_address='https://spot.brooklinema.gov/open311/v2'
        ),
        'Chicago, IL': CityEndpoint(
            name='Chicago, IL',
            root_address='http://311api.cityofchicago.org/open311/v2'
        ),
    }

    @classmethod
    def list_cities(cls) -> List[str]:
        """
        Get the cities with known endpoints.

        Returns:
            List[str]: The list of cities with known endpoints.
        """
        return list(cls._cities.keys())

    @classmethod
    def get(cls, city: str) -> CityEndpoint:
        """
        Get the CityEndpoint object for a given city key.

        Args:
            city (str): The city's key.

        Returns:
            CityEndpoint: The CityEndpoint object for the given city key.
        """
        return cls._cities[city]
