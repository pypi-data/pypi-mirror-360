[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/georeport)](https://badge.fury.io/py/georeport)
[![PyPI version](https://badge.fury.io/py/georeport.svg)](https://badge.fury.io/py/georeport)

# GeoReport
GeoReport is a thin Python wrapper for the Open311 GeoReport v2 API standard.

## Installing GeoReport
GeoReport is available on PyPI:
```
pip install georeport
```

## Example Usage
Get the list of services in a city:
```
from georeport import GeoReport

client = GeoReport.from_city('Brookline, MA')
print(client.get_service_list())
```

Get service requests in a city:
```
from georeport import GeoReport

client = GeoReport.from_city('Chicago, IL')
print(client.get_service_requests())
```

## Supported Features
GeoReport supports retrieval of requests in addition to service lists and definitions. However, GeoReport **does not** currently support the creation of new 311 service requests.
