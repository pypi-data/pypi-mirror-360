import os
import requests
import xmltodict
from typing import List, Dict, Optional
from .cityendpoint import CityEndpoints


class GeoReport:
    """
    Client that holds the necessary data to make API calls to a given
    municipality's Open311 endpoint.

    Args:
        root_address (str): Base address of the API endpoint.
        jurisdiction (Optional[str], optional): The jurisdiction
            (if applicable). Defaults to None.
        api_key (Optional[str], optional): API key for endpoint. Only
            required if creating service requests. Defaults to None.
        output_format (str, optional): Raw output format from API. Must be
            either 'xml' or 'json'. Only applicable if the endpoint does
            not support json. Defaults to 'json'.

    Attributes:
        root_address (str): Base address of the API endpoint.
        jurisdiction (Optional[str], optional): The jurisdiction
            (if applicable). Defaults to None.
        api_key (Optional[str], optional): API key for endpoint. Only
            required if creating service requests. Defaults to None.
        output_format (str, optional): Raw output format from API. Must be
            either 'xml' or 'json'. Only applicable if the endpoint does
            not support json. Defaults to 'json'.

    Raises:
        ValueError: If output_format is not 'xml' or 'json'.
    """
    def __init__(
        self,
        root_address: str,
        jurisdiction: Optional[str] = None,
        api_key: Optional[str] = None,
        output_format: str = 'json'
    ) -> None:
        self.root_address = root_address.rstrip('/')
        self.jurisdiction = jurisdiction
        self.api_key = api_key or os.getenv('GEOREPORT_API_KEY')
        self.output_format = output_format.lower()
        if self.output_format != 'json' and self.output_format != 'xml':
            raise ValueError("output_format must be either 'json' or 'xml'")

    @classmethod
    def from_city(
        cls,
        city: str,
        api_key: Optional[str] = None,
        output_format: str = 'json'
    ) -> 'GeoReport':
        """
        Get the GeoReport object for a known city's endpoint.

        Args:
            city (str): Name of the city.
            pi_key (Optional[str], optional): API key for endpoint. Only
                required if creating service requests. Defaults to None.
            output_format (str, optional): Raw output format from API. Must be
                either 'xml' or 'json'. Only applicable if the endpoint does
                not support json. Defaults to 'json'.

        Returns:
            GeoReport: GeoReport object for that city's Open311 endpoint

        Raises:
            ValueError: If output_format is not 'xml' or 'json'.
        """
        city = CityEndpoints.get(city)
        return cls(
            city.root_address,
            jurisdiction=city.jurisdiction,
            api_key=api_key,
            output_format=output_format
        )

    def get_service_list(self) -> List[Dict]:
        """
        Provide a list of acceptable 311 service request types and their
        associated service codes. These request types can be unique to the
        city/jurisdiction.

        Returns:
            List[Dict]: The services.
        """
        params = {}
        if self.jurisdiction:
            params['jurisdiction_id'] = self.jurisdiction

        response = requests.get(
            f'{self.root_address}/services.{self.output_format}',
            params=params
        )
        response.raise_for_status()

        if self.output_format == 'json':
            return response.json()
        else:
            return xmltodict.parse(response.content)['services']['service']

    def get_service_definition(self, service_code: str) -> Dict:
        """
        Provide attributes associated with a service code. These attributes
        can be unique to the city/jurisdiction.  This call is only necessary
        if the Service selected has metadata set as true from the GET Services
        response.

        Args:
            service_code (str): The service code.

        Returns:
            Dict: The data related to the given service.
        """
        params = {}
        if self.jurisdiction:
            params['jurisdiction_id'] = self.jurisdiction

        response = requests.get(
            f'{self.root_address}/services/{service_code}.'
            f'{self.output_format}',
            params=params
        )
        response.raise_for_status()

        if self.output_format == 'json':
            return response.json()
        else:
            return xmltodict.parse(response.content)['service_definition']

    def get_service_requests(
        self,
        service_request_id: Optional[str] = None,
        service_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        Queries the current status of multiple requests.

        Args:
            service_request_id (Optional[str], optional): To call multiple
                service requests at once, multiple service_request_id can be
                declared; comma delimited. This overrides all other arguments.
                Defaults to None.
            service_code (Optional[str], optional): Specify the service type
                by calling the unique ID of the service_code. This defaults to
                all service codes when not declared; can be declared multiple
                times, comma delimited. Defaults to None.
            start_date (Optional[str], optional): Earliest datetime to include
                in search. When provided with end_date, allows one to search
                for requests which have a requested_datetime that matches a
                given range, but may not span more than 90 days. When not
                specified, the range defaults to most recent 90 days. Must use
                w3 format, eg 2010-01-01T00:00:00Z. Defaults to None.
            end_date (Optional[str], optional): 	Latest datetime to include
                in search. When provided with start_date, allows one to search
                for requests which have a requested_datetime that matches a
                given range, but may not span more than 90 days. When not
                specified, the range defaults to most recent 90 days. Must use
                w3 format, eg 2010-01-01T00:00:00Z. Defaults to None.
            status (Optional[str], optional): 	Allows one to search for
                requests which have a specific status. This defaults to all
                statuses; can be declared multiple times, comma delimited.
                Options: open, closed. Defaults to None.

        Returns:
            List[Dict]: The information contained within the service requests.
        """
        params = {}
        if service_request_id:
            params['service_request_id'] = service_request_id
        if service_code:
            params['service_code'] = service_code
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if status:
            params['status'] = status
        if self.jurisdiction:
            params['jurisdiction_id'] = self.jurisdiction

        response = requests.get(
            f'{self.root_address}/requests.{self.output_format}',
            params=params
        )
        response.raise_for_status()

        if self.output_format == 'json':
            return response.json()
        else:
            data = xmltodict.parse(response.content)
            return data['service_requests']['request']

    def get_service_request(
        self,
        service_request_id: str
    ) -> Dict:
        """
        Query the current status of an individual request.

        Args:
            service_request_id (str): The service request ID.

        Returns:
            Dict: The information contained within the given service request.
        """
        params = {}
        if self.jurisdiction:
            params['jurisdiction_id'] = self.jurisdiction

        response = requests.get(
            f'{self.root_address}/requests/{service_request_id}.'
            f'{self.output_format}',
            params=params
        )
        response.raise_for_status()

        if self.output_format == 'json':
            return response.json()[0]
        else:
            data = xmltodict.parse(response.content)
            return data['service_requests']['request']
