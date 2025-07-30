from inspqcommun.fhir.clients.base_client import BaseClient
from fhirclient.models.immunization import Immunization
from inspqcommun.fhir.visitors.parameters import ParametersVisitor
from requests import Response
import requests
import logging
import json

log = logging.getLogger(__name__)

class ImmunizationClient(BaseClient):

    immunization_endpoint = "{base_url}/Immunization"
    immunization_id_endpoint = "{base_url}/Immunization/{id}"
    immunization_id_override_endpoint = immunization_id_endpoint + '/$override'
    immunization_id_settoforecast_endpoint = immunization_id_endpoint + '/$settoforecast'
    immunization_id_delete_immunization_endpoint = immunization_id_endpoint + '/$delete-immunization'
    def __init__(self, base_url=None, base_uri=None, token_header=None, validate_certs=True) -> None:
        super().__init__(base_url=base_url, base_uri=base_uri, token_header=token_header)
        self.validate_certs = validate_certs

    def create(self, immunization: Immunization) -> Response:
        immunization.meta = None
        response = requests.post(
            url=self.immunization_endpoint.format(base_url=self.get_fhir_url()),
            data=json.dumps(immunization.as_json()),
            headers=self.headers,
            verify=self.validate_certs)
        log.info("POST Immunization : {}".format(response.status_code))
        return response

    def get(self, immunization_id=None) -> Response:
        response = requests.get(
            url=self.immunization_id_endpoint.format(base_url=self.get_fhir_url(),id=immunization_id),
            headers=self.headers,
            verify=self.validate_certs)
        log.info("GET Immunization : {}".format(response.status_code))
        return response
    
    def update(self, immunization: Immunization) -> Response:
        response = requests.put(
            url=self.immunization_id_endpoint.format(base_url=self.get_fhir_url(), id=immunization.id),
            data=json.dumps(immunization.as_json()),
            headers=self.headers,
            verify=self.validate_certs)
        log.info("PUT Immunization : {}".format(response.status_code))
        return response

    def search(self, subject_id=None, code_agent=None, administration_date=None) -> Response:
        params = {}
        if subject_id is not None:
            params['patient'] = subject_id
        if code_agent is not None:
            params['vaccine-code'] = code_agent
        if administration_date is not None:
            params['date'] = administration_date

        response = requests.get(
            url=self.immunization_endpoint.format(base_url=self.get_fhir_url()),
            params=params,
            headers=self.headers,
            verify=self.validate_certs
        )
        log.info("PUT Immunization : {}".format(response.status_code))
        return response

    def override(self, immunization: Immunization) -> Response:
        parametre = ParametersVisitor()
        parametre.add_parameter(valeur=immunization, name='immunization',)
        res = parametre.getFhirResource().as_json()

        response = requests.post(
            url=self.immunization_id_override_endpoint.format(base_url=self.get_fhir_url(), id=immunization.id),
            data=json.dumps(res),
            headers=self.headers,
            verify=self.validate_certs)
        log.info("POST Immunization override : {}".format(response.status_code))
        return response

    def settoforecast(self, immunization: Immunization) -> Response:
        parametre = ParametersVisitor()
        parametre.add_parameter(valeur=immunization, name='immunization',)
        res = parametre.getFhirResource().as_json()

        response = requests.post(
            url=self.immunization_id_settoforecast_endpoint.format(base_url=self.get_fhir_url(), id=immunization.id),
            data=json.dumps(res),
            headers=self.headers,
            verify=self.validate_certs)
        log.info("POST Immunization settoforecast : {}".format(response.status_code))
        return response

    def delete_immunization(self, immunization: Immunization) -> Response:
        parametre = ParametersVisitor()
        parametre.add_parameter(valeur=immunization, name='immunization',)
        res = parametre.getFhirResource().as_json()

        response = requests.post(
            url=self.immunization_id_delete_immunization_endpoint.format(base_url=self.get_fhir_url(), id=immunization.id),
            data=json.dumps(res),
            headers=self.headers,
            verify=self.validate_certs)
        log.info("POST Immunization delete-immunization : {}".format(response.status_code))
        return response

    def extract_immunization_from_response(self, response: Response) -> Immunization:
        if response.status_code == 200 or response.status_code == 201:
            content = json.loads(response.content)
            return Immunization(jsondict=content)
        else:
            return None