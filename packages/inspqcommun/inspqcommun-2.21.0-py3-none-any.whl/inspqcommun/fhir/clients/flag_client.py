from inspqcommun.fhir.clients.base_client import BaseClient
from inspqcommun.fhir.visitors.bundle import BundleVisitor, Bundle
from fhirclient.models.flag import Flag
from requests import Response
import requests
import json
import logging

log = logging.getLogger(__name__)

class FlagClient(BaseClient):
    flag_endpoiunt = "{base_url}/Flag"
    flag_by_id_endpoint = flag_endpoiunt + "/{id}"

    def __init__(self, base_url=None, base_uri=None, token_header=None, validate_certs=True) -> None:
        super().__init__(base_url=base_url, base_uri=base_uri, token_header=token_header)
        self.validate_certs = validate_certs

    def create(self, flag: Flag) -> Response:
        data = json.dumps(flag.as_json())
        response = requests.post(
            url=self.flag_endpoiunt.format(base_url=self.get_fhir_url()),
            data=data,
            headers=self.headers,
            verify=self.validate_certs
        )
        log.info("POST Flag : {}".format(response.status_code))
        return response

    def get_by_id(self, flag_id: int) -> Response:
        response = requests.get(
            url=self.flag_by_id_endpoint.format(base_url=self.get_fhir_url(), id=flag_id),
            headers=self.headers,
            verify=self.validate_certs
        )
        log.info("GET Flag : {}".format(response.status_code))
        return response

    def update(self, flag: Flag) -> Response:
        data = json.dumps(flag.as_json())
        response = requests.put(
            url=self.flag_by_id_endpoint.format(base_url=self.get_fhir_url(), id=flag.id),
            data=data,
            headers=self.headers,
            verify=self.validate_certs
        )
        log.info("PUT Flag : {}".format(response.status_code))
        return response

    def delete(self, flag_id: int) -> Response:
        response = requests.delete(
            url=self.flag_by_id_endpoint.format(base_url=self.get_fhir_url(), id=flag_id),
            headers=self.headers,
            verify=self.validate_certs
        )
        log.info("DELETE Flag : {}".format(response.status_code))  
        return response
    
    def extract_flag_from_response(self, response: Response) -> Flag:
        content = response.json()
        if 'resourceType' in content and content['resourceType'] == 'Flag':
            return Flag(jsondict=content)
        if content['resourceType'] == 'Bundle':
            bundle = BundleVisitor(fhir_resource=Bundle(jsondict=content))
            flags = bundle.get_entries(recurse=True, resource_type='Flag')
            if len(flags) > 0:
                return Flag(jsondict=flags[0])
        return None