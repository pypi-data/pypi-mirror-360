from fhirclient.models.valueset import ValueSet
from inspqcommun.fhir.visitors.base import BaseVisitor
from fhirclient.models.valueset import ValueSetCodeSystemConcept

class ValueSetVisitor(BaseVisitor):
    
    def __init__(self, fhir_resource=None) -> None:
        super().setFhirResource(fhir_resource if fhir_resource else ValueSet())

    def getFhirResource(self) -> ValueSet:
        return super().getFhirResource()

    def search_code_system_concept(self, code=None, display=None) -> ValueSetCodeSystemConcept:
        code_system_concept = None
        if (self.getFhirResource() is not None
                and self.getFhirResource().codeSystem is not None
                and self.getFhirResource().codeSystem.concept is not None
                and len(self.getFhirResource().codeSystem.concept) > 0):
            for concept in self.getFhirResource().codeSystem.concept:
                if ((code is not None and concept.code == code)
                        or (display is not None and concept.display == display)):
                    code_system_concept = concept

        return code_system_concept
    
    def find_code_system_concept_by_code(self, code: str) -> bool:
        return True if self.search_code_system_concept(code=code) else False
    
    def find_code_system_concept_by_display(self, display: str) -> bool:
        return True if self.search_code_system_concept(display=display) else False