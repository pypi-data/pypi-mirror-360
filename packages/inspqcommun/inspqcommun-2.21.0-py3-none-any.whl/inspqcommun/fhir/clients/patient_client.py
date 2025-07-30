import requests
import json
from requests import Response
from fhirclient.models.patient import Patient
from fhirclient.models.coding import Coding
from fhirclient.models.bundle import Bundle
from fhirclient.models.parameters import Parameters
from fhirclient.models.fhirdate import FHIRDate
from inspqcommun.fhir.clients.base_client import BaseClient
from inspqcommun.fhir.visitors.parameters import ParametersVisitor
from datetime import datetime

import logging

log = logging.getLogger(__name__)

class PatientClient(BaseClient):

    base_url = ""
    patient_endpoint = "{0}/Patient"
    patient_id_endpoint = "{0}/Patient/{1}"
    patient_match_endpoint = "{0}/Patient/$match"
    patient_delete_endpoint = patient_id_endpoint + "/$delete-all"
    patient_definir_niu_endpoint = patient_id_endpoint + "/$definir-niu"
    patient_immunization_profile_endpoint = patient_id_endpoint + "/$immunization-profile"
    patient_carnet_vaccinal_endpoint = patient_id_endpoint + "/$carnet-vaccinal"
    patient_preuve_vaccination_endpoint = patient_id_endpoint + "/$preuve-vaccination"
    _covid_19_agent_code = "QCSNOMED00124"
    _covid_19_agent_display = "COVID-19"
    _preuve_vaccination_default_agent: Coding
    _default_coding_system = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary'
    _default_coding_version = "1.0.0"


    def __init__(self, base_url=None, base_uri=None, token_header=None, validate_certs=True) -> None:
        super().__init__(base_url=base_url,token_header=token_header, base_uri=base_uri)
        self.validate_certs = validate_certs
        if base_url is not None:
            self.base_url = base_url
        self._preuve_vaccination_default_agent = Coding()
        self._preuve_vaccination_default_agent.code = self._covid_19_agent_code
        self._preuve_vaccination_default_agent.display = self._covid_19_agent_display
        self._preuve_vaccination_default_agent.system = self._default_coding_system
        self._preuve_vaccination_default_agent.version = self._default_coding_version

    def create(self, patient: Patient):
        response = requests.post(
            url=self.patient_endpoint.format(self.get_fhir_url()),
            data=json.dumps(patient.as_json()),
            headers=self.headers,
            verify=self.validate_certs)
        log.info("POST Patient : {}".format(response.status_code))
        return response

    def update(self, patient: Patient):
        response = requests.put(
            url=self.patient_id_endpoint.format(self.get_fhir_url(), patient.id),
            data=json.dumps(patient.as_json()),
            headers=self.headers,
            verify=self.validate_certs)
        log.info("PUT Patient : {}".format(response.status_code))
        return response

    def get_by_id(self, patient_id=None):
        response = requests.get(url=self.patient_id_endpoint.format(self.get_fhir_url(), patient_id), headers=self.headers, verify=self.validate_certs)
        log.info("GET Patient/{} : {}".format(patient_id, response.status_code if response.status_code else 404))
        return response

    def match(self, patient: Patient):
        parametre = ParametersVisitor()
        parametre.add_parameter(patient)
        res = parametre.getFhirResource().as_json()
        response = requests.post(url=self.patient_match_endpoint.format(self.get_fhir_url()), data=json.dumps(res), headers=self.headers, verify=self.validate_certs)
        log.info("POST Patient/$match : {}".format(response.status_code))
        return response

    def search(self, identifier=None, nam=None, given=None, family=None, gender=None, birthdate=None):
        params = {}
        if identifier is not None:
            params['identifier'] = identifier
        elif nam is not None:
            params['identifier'] = "code=NAM|{}".format(nam)
        if given is not None:
            params['given'] = given
        if family is not None:
            params['family'] = family
        if gender is not None:
            params['gender'] = gender
        if birthdate is not None:
            birthdate_param = birthdate.isostring if type(birthdate) is FHIRDate else birthdate
            params['birthdate'] = birthdate_param

        response = requests.get(url=self.patient_endpoint.format(self.get_fhir_url()), params=params, headers=self.headers, verify=self.validate_certs)
        log.info("GET Patient?{} : {}".format("&".join([ key + "=" + str(params[key]) for key in params ]), response.status_code))
        return response

    def delete(self, patient_id: int, if_modified_since: datetime=None) -> Response:
        if if_modified_since is not None:
            self.headers['If-Modified-Since'] = datetime.strftime(if_modified_since, "%Y-%m-%dT%H:%M:%S")
        response = requests.post(url=self.patient_delete_endpoint.format(self.get_fhir_url(), patient_id), headers=self.headers, verify=self.validate_certs)
        log.info("DELETE Patient/{} : {}".format(patient_id, response.status_code))
        return response
    
    def extract_patient_from_response(self, response: Response) -> Patient:
        content_dict = json.loads(response.content)
        if (content_dict['resourceType'] == 'Parameters'):
            params = Parameters(jsondict=content_dict)
            if params is not None and params.parameter is not None:
                for param in params.parameter:
                    if type(param.resource) is Patient:
                        return param.resource
        else:
            return Patient(jsondict=content_dict)
        
    def extract_patient_bundle_from_response(self, response: Response) -> Bundle:
        json_resource = json.loads(response.content.decode())
        if (json_resource['resourceType'] == 'Bundle'):
            return Bundle(jsondict=json.loads(response.content))
        return None
    
    def get_immunization_profile(self, patient_id: int):
        
        url = self.patient_immunization_profile_endpoint.format(self.get_fhir_url(), patient_id)
        response = requests.get(url=url, headers=self.headers, verify=self.validate_certs)
        return response

    def get_carnet_vaccinal(self, patient_id: int, accept: str=None) -> Response:
        url = self.patient_carnet_vaccinal_endpoint.format(self.get_fhir_url(), patient_id)
        headers = self.headers
        if accept is not None:
            headers['Accept'] = accept
        response = requests.get(url=url, headers=headers, verify=self.validate_certs)
        return response

    def get_preuve_vaccination(self, patient_id: int, agent: Coding=None, actif_seulement: bool=True) -> Response:
        if agent is None:
            agent = self._preuve_vaccination_default_agent
        param = ParametersVisitor()
        param.add_parameter(name="actifSeulement", valeur=actif_seulement)
        param.add_parameter(name="agent", valeur=agent)
        data = param.getFhirResource().as_json()
        url = self.patient_preuve_vaccination_endpoint.format(
            self.get_fhir_url(), patient_id)
        response = requests.post(
            url=url,
            data=json.dumps(data),
            headers=self.headers,
            verify=self.validate_certs)
        return response
    
