from fhirclient.models.practitioner import Practitioner
from inspqcommun.fhir.visitors.bundle import BundleVisitor, Bundle
from inspqcommun.fhir.clients.base_client import BaseClient
from requests import Response

import requests
import json
import logging

log = logging.getLogger(__name__)

class PractitionerClient(BaseClient):

    practitioner_endpoint = "{base_url}/Practitioner"
    practitioner_by_id_endpoint = practitioner_endpoint + "/{id}"

    def __init__(self, base_url=None, base_uri=None, token_header=None, validate_certs=True) -> None:
        super().__init__(base_url=base_url, base_uri=base_uri, token_header=token_header)
        self.validate_certs = validate_certs

    def search(self, identifier=None, role=None, family=None, given=None):
        params = {}
        if identifier is not None:
            params["identifier"] = identifier
        if role is not None:
            params["role"] = role
        if family is not None:
            params["family"] = family
        if given is not None:
            params["given"] = given

        response = requests.get(
            url=self.practitioner_endpoint.format(base_url=self.get_fhir_url()),
            headers=self.headers,
            params=params,
            verify=self.validate_certs)
        log.info("GET Practitioner?{} : {}".format("&".join([ key + "=" + params[key] for key in params ]), response.status_code))
        return response

    def get_by_id(self, practitioner_id=None):
        response = None
        if practitioner_id is not None:
            response = requests.get(
                url=self.practitioner_by_id_endpoint.format(base_url=self.get_fhir_url(), id=practitioner_id),
                headers=self.headers,
                verify=self.validate_certs
            )
        log.info("GET Organization/{} : {}".format(practitioner_id, response.status_code if response.status_code else 404))
        return response

    def extract_practitioner_bundle_from_response(self, practitioner_response: Response) -> Bundle:
        if practitioner_response.status_code == 200:
            content_dict = json.loads(practitioner_response.content)
            return Bundle(jsondict=content_dict)
        return None
    
    def extract_practitioner_from_response(self, response: Response) -> Practitioner:
        practitioner: Practitioner = None

        if response.status_code == 200:
            content_dict = json.loads(response.content)
            if "resourceType" in content_dict and content_dict["resourceType"] == "Bundle":
                bundle = BundleVisitor(
                    fhir_resource=self.extract_practitioner_bundle_from_response(response))
                practitioners = bundle.get_entries(recurse=True, resource_type="Practitioner")
                if len(practitioners) > 0:
                    practitioner = practitioners[0]
                return practitioner
            elif "resourceType" in content_dict and content_dict["resourceType"] == "Practitioner":
                practitioner = Practitioner(jsondict=content_dict)
            
        return practitioner