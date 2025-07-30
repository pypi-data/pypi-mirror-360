from fhirclient.models.location import Location
from fhirclient.models.bundle import Bundle
from inspqcommun.fhir.clients.base_client import BaseClient
from requests import Response
import requests
import json
import logging

log = logging.getLogger(__name__)

class LocationClient(BaseClient):

    location_endpoint = "{base_url}/Location"
    location_by_id_endpoint = location_endpoint + "/{id}"

    def __init__(self, base_url=None, base_uri=None, token_header=None, validate_certs=True) -> None:
        super().__init__(base_url=base_url, base_uri=base_uri, token_header=token_header)
        self.validate_certs = validate_certs

    def search(self, name=None, address_city=None, identifier=None):
        params = {}
        if name is not None:
            params['name'] = name
        if identifier is not None:
            params['identifier'] = identifier
        if address_city is not None:
            params['address-city'] = address_city
        response = requests.get(
            url=self.location_endpoint.format(base_url=self.get_fhir_url()),
            params=params,
            headers=self.headers,
            verify=self.validate_certs)
        log.info("GET Location?{} : {}".format("&".join([ key + "=" + params[key] for key in params ]), response.status_code))
        return response

    def get_by_id(self, location_id=None):
        response = None
        if location_id is not None:
            response = requests.get(
                url=self.location_by_id_endpoint.format(base_url=self.get_fhir_url(), id=location_id),
                headers=self.headers,
                verify=self.validate_certs)
        
        log.info("GET Location/{} : {}".format(location_id, response.status_code if response.status_code else 404))
        return response

    def get_all(self, page=0, page_size=10):
        page_params = {
            "page": page,
            "size": page_size
        }
        response = requests.get(url="{0}/_list".format(self.location_endpoint.format(base_url=self.get_fhir_url())),
                                params=page_params,
                                headers=self.headers,
                                verify=self.validate_certs)
        log.info("GET Location/_list : {}".format(response.status_code))
        return response
    
    def create(self, location: Location):
        response =  requests.post(
            url=self.location_endpoint.format(base_url=self.get_fhir_url()),
            data=json.dumps(location.as_json()),
            headers=self.headers,
            verify=self.validate_certs)
        log.info("POST Location : {}".format(response.status_code))
        return response

    def update(self, location: Location):
        response = requests.put(
            url=self.location_by_id_endpoint.format(base_url=self.get_fhir_url(), id=location.id),
            data=json.dumps(location.as_json()),
            headers=self.headers,
            verify=self.validate_certs)
        log.info("PUT Location/{} : {}".format(location.id, response.status_code))
        return response

    def delete(self, location: Location = None, id: int = None):
        if location or id:
            response = requests.delete(
                url=self.location_by_id_endpoint.format(base_url=self.get_fhir_url(), id=location.id if location else id),
                headers=self.headers,
                verify=self.validate_certs)
            log.info("DELETE Location/{} : {}".format(location.id if location else id, response.status_code))
            return response
        else:
            log.warn("DELETE Location - aucun id spécifié")
            return None
    
    def extract_location_bundle_from_response(self, response: Response) -> Bundle:
        if response.status_code == 200:
            content_dict = json.loads(response.content)
            return Bundle(jsondict=content_dict)
        else:
            return None
    
    def extract_location_from_response(self, response: Response) -> Location:
        if response.status_code == 200 or response.status_code == 201:
            content = json.loads(response.content)
            if "entry" in content and len(content["entry"]) > 0:
                return Location(jsondict=content["entry"][0]["resource"])
            elif "resourceType" in content and content["resourceType"] == "Location":
                return Location(jsondict=content)
        return None