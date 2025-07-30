import logging
from inspqcommun.fhir.clients.base_client import BaseClient
from fhirclient.models.condition import Condition
from requests import Response
import requests
import json

log = logging.getLogger(__name__)
class ConditionClient(BaseClient):
    condition_endpoint = "{base_url}/Condition"
    condition_id_endpoint = "{base_url}/Condition/{id}"
    def __init__(self, base_url=None, base_uri=None, token_header=None, validate_certs=True) -> None:
        super().__init__(base_url=base_url, base_uri=base_uri, token_header=token_header)
        self.validate_certs = validate_certs


    def get_by_id(self, condition_id: int) -> Response:
        response = requests.get(
            url=self.condition_id_endpoint.format(base_url=self.get_fhir_url(), id=condition_id),
            headers=self.headers,
            verify=self.validate_certs
        )
        log.info("GET Condition : {}".format(response.status_code))
        return response

    def create(self, condition: Condition) -> Response:
        data = json.dumps(condition.as_json())
        response = requests.post(
            url=self.condition_endpoint.format(base_url=self.get_fhir_url()),
            data=data,
            headers=self.headers,
            verify=self.validate_certs
        )
        log.info("POST Condition : {}".format(response.status_code))
        return response

    def update(self, condition_id, condition: Condition) -> Response:
        response = requests.put(
            url=self.condition_id_endpoint.format(base_url=self.get_fhir_url(), id=condition_id),
            data=json.dumps(condition.as_json()),
            headers=self.headers,
            verify=self.validate_certs
        )
        log.info("PUT Condition : {}".format(response.status_code))
        return response
    
    def extract_condition_from_response(self, response: Response) -> Condition:
        content = response.json()
        if 'resourceType' in content and content['resourceType'] == 'Condition':
            return Condition(jsondict=content)
        if content['resourceType'] == 'Bundle':
            for entry in content['entry']:
                if 'resource' in entry and entry['resource']['resourceType'] == 'Condition':
                    return Condition(jsondict=entry['resource'])