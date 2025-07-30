from fhirclient.models.medication import Medication
from inspqcommun.fhir.clients.base_client import BaseClient
from requests import Response
import requests
import json
import logging

log = logging.getLogger(__name__)

class MedicationClient(BaseClient):

    medication_endpoint = "{base_url}/Medication"
    get_by_trade_name_endpoint = medication_endpoint + "/{trade_name}"

    def __init__(self, base_url=None, base_uri=None, token_header=None, validate_certs=True) -> None:
        super().__init__(base_url=base_url, base_uri=base_uri, token_header=token_header)
        self.validate_certs = validate_certs

    def get_by_trade_name(self, trade_name):
        response = requests.get(
            url=self.get_by_trade_name_endpoint.format(base_url=self.get_fhir_url(), trade_name=trade_name),
            headers=self.headers,
            verify=self.validate_certs)
        log.info("GET Medication/{} : {}".format(trade_name, response.status_code))
        return response
    
    def extract_medication_from_response(self, medication_response: Response) -> Medication:
        if medication_response.status_code == 200:
            medication_dict = json.loads(medication_response.content)
            return Medication(jsondict=medication_dict)
        else:
            return None
            