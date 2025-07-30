from fhirclient.models.organization import Organization
from fhirclient.models.bundle import Bundle
from inspqcommun.fhir.clients.base_client import BaseClient
from requests import Response
import requests
import json
import logging

log = logging.getLogger(__name__)

class OrganizationClient(BaseClient):
    
    organization_endpoint = "{base_url}/Organization"
    search_endpoint = organization_endpoint + "/_search"
    organization_by_id_endpoint = organization_endpoint + "/{id}"

    def __init__(self, base_url=None, base_uri=None, token_header=None, validate_certs=True) -> None:
        super().__init__(base_url=base_url, base_uri=base_uri, token_header=token_header)
        self.validate_certs = validate_certs

    def search(self, name=None, identifier=None):
        params = {}
        if name is not None:
            params['name'] = name
        if identifier is not None:
            params['identifier'] = identifier
        response = requests.get(url=self.organization_endpoint.format(base_url=self.get_fhir_url()), params=params, headers=self.headers, verify=self.validate_certs)
        log.info("GET Organization?{} : {}".format("&".join([ key + "=" + params[key] for key in params ]), response.status_code))
        return response

    def get_by_id(self, org_id=None):
        response = None
        if org_id is not None:
            url = self.organization_by_id_endpoint.format(base_url=self.get_fhir_url(), id=org_id)
            response = self.__get_by_url(url=url)
        
        log.info("GET Organization/{} : {}".format(org_id, response.status_code if response.status_code else 404))
        return response
        
    def get_by_reference(self, reference=None):
        response = None
        if reference is not None:
            url = "{0}/{1}".format(self.get_fhir_url(), reference.reference)
            response = self.__get_by_url(url=url)
        
        log.info("GET Organization/{} : {}".format(reference.reference if reference is not None else '', response.status_code if response.status_code else 404))
        return response

    def get_all(self, page=0, page_size=10):
        page_params = {
            "page": page,
            "size": page_size
        }
        response = requests.get(url="{0}/_list".format(self.organization_endpoint.format(base_url=self.get_fhir_url())),
                                params=page_params,
                                headers=self.headers,
                                verify=self.validate_certs)
        log.info("GET Organization/_list : {}".format(response.status_code))
        return response
    
    def create(self, organization: Organization):
        response = requests.post(
            url=self.organization_endpoint.format(base_url=self.get_fhir_url()),
            data=json.dumps(organization.as_json()),
            headers=self.headers,
            verify=self.validate_certs)
        log.info("POST Organization : {}".format(response.status_code))
        return response

    def update(self, organization: Organization):
        response = requests.put(
            url=self.organization_by_id_endpoint.format(base_url=self.get_fhir_url(), id=organization.id),
            data=json.dumps(organization.as_json()),
            headers=self.headers,
            verify=self.validate_certs)
        log.info("PUT Organization/{} : {}".format(organization.id, response.status_code))
        return response

    def delete(self, organization: Organization = None, id = None):
        if organization or id:
            response = requests.delete(
                url=self.organization_by_id_endpoint.format(base_url=self.get_fhir_url(), id=organization.id if organization else id),
                headers=self.headers,
                verify=self.validate_certs)
            log.info("DELETE Organization/{} : {}".format(organization.id if organization else id, response.status_code))
            return response
        else:
            log.warn("DELETE Location - aucun id spécifié")
            return None

    def extract_organization_from_response(self, response: Response) -> Organization:
        if response.status_code == 200 or response.status_code == 201:
            content_dict = json.loads(response.content)
            return Organization(jsondict=content_dict)
        
    def extract_organization_bundle_from_response(self, response: Response) -> Bundle:
        if response.status_code == 200:
            content_dict = json.loads(response.content)
            return Bundle(jsondict=content_dict)
        return None
    
    def __get_by_url(self, url):        
        response = requests.get(
            url=url,
            headers=self.headers,
            verify=self.validate_certs
        )
        return response