from fhirclient.models.immunization import Immunization
from fhirclient.models.patient import Patient
from fhirclient.models.bundle import Bundle, BundleEntry,BundleEntryRequest
from fhirclient.models.reference import Reference
import requests
import json
import logging
import uuid
from requests import Response

log = logging.getLogger(__name__)

class BaseClient:

    base_headers = {
        "Content-type": "application/json+fhir"
    }

    def __init__(self, base_url=None, base_uri=None, token_header=None, validate_certs=True) -> None:
        self.base_url = base_url if base_url is not None else "http://localhost:14001"
        self.base_uri = base_uri if base_uri is not None else ""
        self.validate_certs = validate_certs
        self.set_headers(token_header=token_header)

    def set_headers(self, headers={}, token_header=None):
        new_headers = {**headers, **self.base_headers}
        if token_header is not None:
            if 'Content-Type' in token_header:
                del token_header['Content-Type']
            headers_with_auth = {**new_headers, **token_header}
            self.headers = headers_with_auth
        else:
            self.headers = new_headers
        return self.headers
    
    def get_fhir_url(self):
        return "{0}{1}".format(self.base_url, self.base_uri)
    
    def create_patient_with_immunization(self, patient:Patient, immunization:Immunization) -> Response:
        bundle = Bundle()
        bundle.type = 'transaction'
        entries = []
        patient_entry = BundleEntry()
        patient_entry.resource = patient
        patient_uuid = uuid.uuid4()
        patient_full_url = "urn:uuid:{uuid}".format(uuid=patient_uuid)
        patient_entry.fullUrl = patient_full_url
        patient_entry.request = BundleEntryRequest(jsondict={'method':'POST', 'url': 'Patient'})
        entries.append(patient_entry)
        immunization.patient = Reference(jsondict={'reference': patient_full_url})
        immunization_entry = BundleEntry()
        immunization_uuid = uuid.uuid4()
        immunization_full_url = "urn:uuid:{uuid}".format(uuid=immunization_uuid)
        immunization_entry.fullUrl = immunization_full_url
        immunization_entry.resource = immunization
        immunization_entry.request = BundleEntryRequest(jsondict={'method': 'POST', 'url': 'Immunization'})
        entries.append(immunization_entry)
        bundle.entry = entries
        data = json.dumps(bundle.as_json())
        response = requests.post(
            url="{base_url}/".format(base_url=self.get_fhir_url()),
            data=data,
            headers=self.headers,
            verify=self.validate_certs)
        log.info("POST Base URL : {}".format(response.status_code))
        return response

