from inspqcommun.fhir.visitors.base import BaseVisitor
from fhirclient.models.flag import Flag
from fhirclient.models.reference import Reference
from fhirclient.models.coding import Coding
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.period import Period
from fhirclient.models.fhirdate import FHIRDate
from dateutil.parser import parse

class FlagVisitor(BaseVisitor):
    def __init__(self, fhir_resource: Flag = None) -> None:
        self.setFhirResource(fhir_resource if fhir_resource else Flag())

    def getFhirResource(self) -> Flag:
        return super().getFhirResource()
    
    def get_id(self) -> int:
        return self.getFhirResource().id
    
    def set_id(self, id: str) -> None:
        self.getFhirResource().id = id 

    def set_subject_id(self, id: str) -> None:
        reference = Reference()
        reference.reference = id
        self.getFhirResource().subject = reference

    def get_subject_id(self) -> str:
        return self.getFhirResource().subject.reference
    
    def get_category(self) -> Coding:
        if self.getFhirResource().category:
            for coding in self.getFhirResource().category.coding:
                if coding.system == self.DEFAULT_CODING_SYSTEM and coding.version == self.DEFAULT_CODING_VERSION:
                    return coding
        return None
    
    def set_category(self, coding: Coding) -> None:
        if coding.system is None:
            coding.system = self.DEFAULT_CODING_SYSTEM
        if coding.version is None:
            coding.version = self.DEFAULT_CODING_VERSION
        self.getFhirResource().category = CodeableConcept()
        self.getFhirResource().category.coding = [coding]

    def get_period(self) -> Period:
        return self.getFhirResource().period
    
    def set_period(self, period: Period) -> None:
        self.getFhirResource().period = period

    def set_period_start_date(self, start_date: FHIRDate) -> None:
        period = self.get_period()
        if period is None:
            period = Period()
        period.start = start_date
        self.set_period(period)

    def set_period_start_date_from_str(self, start_date: str) -> None:
        period_start_date = FHIRDate()
        period_start_date.date = parse(start_date)
        self.set_period_start_date(start_date=period_start_date)

    def set_period_end_date(self, end_date: FHIRDate) -> None:
        period = self.get_period()
        if period is None:
            period = Period()
        period.end = end_date
        self.set_period(period)

    def set_period_end_date_from_str(self, end_date: str) -> None:
        period_end_date = FHIRDate()
        period_end_date.date = parse(end_date)
        self.set_period_end_date(end_date=period_end_date)

    def get_code(self) -> Coding:
        if self.getFhirResource().code:
            for coding in self.getFhirResource().code.coding:
                if coding.system == self.DEFAULT_CODING_SYSTEM and coding.version == self.DEFAULT_CODING_VERSION:
                    return coding
        return None
    
    def set_code(self, coding: Coding) -> None:
        if coding.system is None:
            coding.system = self.DEFAULT_CODING_SYSTEM
        if coding.version is None:
            coding.version = self.DEFAULT_CODING_VERSION
        self.getFhirResource().code = CodeableConcept()
        self.getFhirResource().code.coding = [coding]

    