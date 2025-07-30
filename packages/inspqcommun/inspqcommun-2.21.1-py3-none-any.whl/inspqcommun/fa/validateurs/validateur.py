from inspqcommun.fhir.visitors.value_set import ValueSetVisitor
from inspqcommun.fhir.clients.value_set_client import ValueSetClient
from requests import Response
import logging

log = logging.getLogger(__name__)

class Validateur:

    def __init__(self, value_set_client: ValueSetClient) -> None:
        self._value_set_client = value_set_client

    def _code_present_dans_domaine_vocabulaire(self, code: str, response: Response) -> bool:
        if response.status_code == 200:
            value_set = self._value_set_client.extract_value_set_from_response(response)
            return ValueSetVisitor(value_set).find_code_system_concept_by_code(code)
        else:
            log.error("Erreur lors de l'appel aux Fonctions allégées: {} {}".format(response.status_code, response.content))
            return False
    
    def _description_presente_dans_domaine_vocabulaire(self, description: str, response: Response) -> bool:
        if response.status_code == 200:
            value_set = self._value_set_client.extract_value_set_from_response(response)
            return ValueSetVisitor(value_set).find_code_system_concept_by_display(description)
        else:
            log.error("Erreur lors de l'appel aux Fonctions allégées: {} {}".format(response.status_code, response.content))
            return False