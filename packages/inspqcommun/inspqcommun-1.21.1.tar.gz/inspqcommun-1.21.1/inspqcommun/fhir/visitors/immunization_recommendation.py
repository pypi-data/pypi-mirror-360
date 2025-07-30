from inspqcommun.fhir.visitors.base import BaseVisitor
from fhirclient.models.immunizationrecommendation import ImmunizationRecommendation, ImmunizationRecommendationRecommendation
from fhirclient.models.fhirreference import FHIRReference
from fhirclient.models.coding import Coding

class ImmunizationRecommendationVisitor(BaseVisitor):
    def __init__(self, fhir_resource: ImmunizationRecommendation=None) -> None:
        self.setFhirResource(fhir_resource if fhir_resource else ImmunizationRecommendation())

    def getFhirResource(self) -> ImmunizationRecommendation:
        return super().getFhirResource()
    
    def get_id(self) -> str:
        return self.getFhirResource().id
    
    def set_id(self, id: str) -> None:
        self.getFhirResource().id = id

    def get_patient_id(self) -> str:
        return self.getFhirResource().patient.id
    
    def set_patient_id(self, id: str) -> None:
        ref = FHIRReference()
        ref.id = id
        self.getFhirResource().patient = ref

    def get_recommendations(self)-> list[ImmunizationRecommendationRecommendation]:
        return self.getFhirResource().recommendation
    
    def get_recommendation_vaccine_code(self, index: int=0) -> Coding:
        for coding in self.getFhirResource().recommendation[index].vaccineCode.coding:
            if coding.system == self.DEFAULT_CODING_SYSTEM and coding.version == self.DEFAULT_CODING_VERSION:
                return coding
        return None
    
    def get_recommendation_forecast_status(self, index: int=0) -> Coding:
        for coding in self.getFhirResource().recommendation[index].forecastStatus.coding:
            if coding.system == self.DEFAULT_CODING_SYSTEM and coding.version == self.DEFAULT_CODING_VERSION:
                return coding
        return None