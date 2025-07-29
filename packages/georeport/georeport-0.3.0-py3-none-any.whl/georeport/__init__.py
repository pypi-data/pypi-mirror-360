import importlib.metadata

__version__ = importlib.metadata.version('georeport')

from .georeport import GeoReport
from .cityendpoint import CityEndpoints, CityEndpoint
