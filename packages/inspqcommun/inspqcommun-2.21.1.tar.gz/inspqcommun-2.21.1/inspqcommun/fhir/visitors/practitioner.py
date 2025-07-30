from fhirclient.models.practitioner import Practitioner
from fhirclient.models.humanname import HumanName
from inspqcommun.fhir.visitors.base import BaseVisitor

class PractitionerVisitor(BaseVisitor):

    def __init__(self, fhir_resource=None) -> None:
        self.setFhirResource(fhir_resource=fhir_resource if fhir_resource else Practitioner())

    def getFhirResource(self) -> Practitioner:
        return super().getFhirResource()
    
    def get_id(self):
        return self.getFhirResource().id
    
    def get_family(self):
        if type(self.getFhirResource().name) is HumanName:
            return self.getFhirResource().name.family
        return None

    def get_given(self):
        if type(self.getFhirResource().name) is HumanName:
            return self.getFhirResource().name.given
        return None

    