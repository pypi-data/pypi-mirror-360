from fhirclient.models.operationoutcome import OperationOutcome
from fhirclient.models.coding import Coding
from inspqcommun.fhir.visitors.base import BaseVisitor

class OperationOutcomeVisitor(BaseVisitor):
    __message_code_url = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extension/#operationoutcome/messagecode'
    def __init__(self, fhir_resource=None) -> None:

        self.setFhirResource(fhir_resource if fhir_resource else OperationOutcome())

    def getFhirResource(self) -> OperationOutcome:
        return super().getFhirResource()

    def get_issue_count(self) -> int:
        return len(self.getFhirResource().issue)

    def get_issue_code(self, index: int=0) -> str:
        return self.getFhirResource().issue[index].code

    def get_issue_severity(self, index: int=0):
        return self.getFhirResource().issue[index].severity

    def get_issue_details(self, index: int=0) -> Coding:
        details = self._get_coding_par_system(self.getFhirResource().issue[index].details)
        return details if details else self.getFhirResource().issue[index].details[0]
    
    def get_issue_message_code(self, index: int=0) -> str: 
        for ext in self.getFhirResource().issue[index].extension:
            if ext.url == self.__message_code_url:
                return ext.valueString
        return None
    
    def get_issue_diagnostics(self, index: int=0) -> str:
        return self.getFhirResource().issue[index].diagnostics