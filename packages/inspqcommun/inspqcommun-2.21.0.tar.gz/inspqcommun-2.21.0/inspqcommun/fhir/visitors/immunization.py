from fhirclient.models.meta import Meta
from fhirclient.models.extension import Extension
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models.coding import Coding
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.patient import Patient
from fhirclient.models.immunization import Immunization, ImmunizationExplanation
from fhirclient.models.location import Location
from fhirclient.models.practitioner import Practitioner
from fhirclient.models.quantity import Quantity
from fhirclient.models.reference import Reference

from inspqcommun.fhir.visitors.base import BaseVisitor

from datetime import date, datetime
from typing import List

class ImmunizationVisitor(BaseVisitor):
        
    OVERRIDE_STATUS_URL = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/overridestatus"
    OVERRIDE_REASON_URL = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/overridereason"
    REASON_FOR_DELETION_URL = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/reasonfordeletion"
    OTHER_REASON_FOR_DELETION_URL = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/otherreasonfordeletion"
    ANTIGEN_STATUS_ANTIGEN_URL = "antigen"
    ANTIGEN_STATUS_STATUS_URL = "status"
    ANTIGEN_STATUS_DOSE_NUMER_URL = "doseNumber"
    LOT_ID_URL = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/lotid"
    TRADE_NAME_URL = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/tradename'
    ANTIGEN_STATUS_URL = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/antigenstatus"
    PROFILE_URL = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/profiles/InspqImmunization.structuredefinition.xml'
    UPDATED_BY_URL = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#common/updatedby"
    CREATED_BY_URL = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#common/createdby'
    CREATION_DATE_URL = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#common/creationdate'

    def __init__(self, fhir_resource=None) -> None:
        self.setFhirResource(fhir_resource=fhir_resource if fhir_resource else self.__build_default_immunization())
    
    def __build_default_immunization(self) -> Immunization:
        immunization = Immunization()
        immunization.wasNotGiven = False
        immunization.status = 'completed'
        return immunization

    def getFhirResource(self) -> Immunization:
        return super().getFhirResource()  
    
    def set_id(self, id=None):
        self.getFhirResource().id = id

    def get_id(self):
        return self.getFhirResource().id
        
    def get_meta_updated_by(self):
        if self.getFhirResource() is None or self.getFhirResource().meta is None or self.getFhirResource().meta.extension is None:
            return None
        for extension in self.getFhirResource().meta.extension:
            if extension.url == self.UPDATED_BY_URL:
                return extension.valueString
        return None

    def get_meta_created_by(self):
        if self.getFhirResource() is None or self.getFhirResource().meta is None or self.getFhirResource().meta.extension is None:
            return None
        for extension in self.getFhirResource().meta.extension:
            if extension.url == self.CREATED_BY_URL:
                return extension.valueString
        return None

    def get_meta_creation_date(self):
        if self.getFhirResource() is None or self.getFhirResource().meta is None or self.getFhirResource().meta.extension is None:
            return None
        for extension in self.getFhirResource().meta.extension:
            if extension.url == self.CREATION_DATE_URL:
                return extension.valueDate
        return None

    def get_meta_version_id(self):
        if self.getFhirResource() is None or self.getFhirResource().meta is None:
            return None
        return self.getFhirResource().meta.versionId

    def get_meta_last_updated(self):
        if self.getFhirResource() is None or self.getFhirResource().meta is None:
            return None
        if self.getFhirResource().meta.lastUpdated is not None:
            return self.getFhirResource().meta.lastUpdated.isostring
        else:
            return self.getFhirResource().meta.lastUpdated

    def get_meta_profile(self):
        if self.getFhirResource() is None or self.getFhirResource().meta is None:
            return None
        return self.getFhirResource().meta.profile
    
    def set_meta_updated_by(self, updated_by: str = None):
        if not self.getFhirResource().meta:
            self.getFhirResource().meta = Meta()
        if not self.getFhirResource().meta.extension:
            self.getFhirResource().meta.extension = []
        self.getFhirResource().meta.extension = super().add_or_update_extension_to_extensions(extension=self._creer_extension(url=self.UPDATED_BY_URL, valueString=updated_by), 
                                                                                              extensions=self.getFhirResource().meta.extension)
    def set_meta_last_updated(self, last_updated: date = None):
        if not self.getFhirResource().meta:
            self.getFhirResource().meta = Meta()
        self.getFhirResource().meta.lastUpdated = last_updated
    
    def set_meta_created_by(self, created_by: str = None):
        if not self.getFhirResource().meta:
            self.getFhirResource().meta = Meta()
        if not self.getFhirResource().meta.extension:
            self.getFhirResource().meta.extension = []
        self.getFhirResource().meta.extension = super().add_or_update_extension_to_extensions(extension=self._creer_extension(url=self.CREATED_BY_URL, valueString=created_by),
                                                                                              extensions=self.getFhirResource().meta.extension)
        
    def set_meta_creation_date(self, creation_date: date = None):
        if not self.getFhirResource().meta:
            self.getFhirResource().meta = Meta()
        if not self.getFhirResource().meta.extension:
            self.getFhirResource().meta.extension = []
        self.getFhirResource().meta.extension = super().add_or_update_extension_to_extensions(extension=self._creer_extension(url=self.CREATION_DATE_URL, valueDate=creation_date),
                                                                                              extensions=self.getFhirResource().meta.extension)
    
    def set_meta_profile(self, profile: str = None):
        if not self.getFhirResource().meta:
            self.getFhirResource().meta = Meta()
        self.getFhirResource().meta.profile = [ profile ]

    def set_meta_version_id(self, version_id: str = None):
        if not self.getFhirResource().meta:
            self.getFhirResource().meta = Meta()
        self.getFhirResource().meta.versionId = version_id

    def get_override_status(self) -> CodeableConcept:
        if self.getFhirResource().extension is not None:
            for ext in self.getFhirResource().extension:
                if ext.url == self.OVERRIDE_STATUS_URL:
                    return ext.valueCodeableConcept
        return None

    def set_override_status(self, status_code:str=None, status_display:str=None):
        status_codeable_concept = self._to_codeable_concept(
            code=status_code,
            display=status_display,
            coding_system=ImmunizationVisitor.DEFAULT_CODING_SYSTEM,
            coding_version=ImmunizationVisitor.DEFAULT_CODING_VERSION)
        self.getFhirResource().extension = super().add_or_update_extension_to_extensions(extension=self._creer_extension(self.OVERRIDE_STATUS_URL, valueCodeableConcept=status_codeable_concept), 
                                                                                         extensions=self.getFhirResource().extension)

    def get_override_reason(self) -> CodeableConcept:
        if self.getFhirResource().extension is not None:
            for ext in self.getFhirResource().extension:
                if ext.url == self.OVERRIDE_REASON_URL:
                    return ext.valueCodeableConcept
        return None

    def set_override_reason(self, reason_code:str=None, status_display:str=None):
        status_codeable_concept = self._to_codeable_concept(
            code=reason_code,
            display=status_display,
            coding_system=ImmunizationVisitor.DEFAULT_CODING_SYSTEM,
            coding_version=ImmunizationVisitor.DEFAULT_CODING_VERSION)
        self.getFhirResource().extension = super().add_or_update_extension_to_extensions(extension=self._creer_extension(self.OVERRIDE_REASON_URL, valueCodeableConcept=status_codeable_concept), 
                                                                                         extensions=self.getFhirResource().extension)

    def set_antigen_status(self, antigen_code:str=None, antigen_display:str=None, dose_number:int=None, status_code:str=None, status_display:str=None):
        antigen_status_ext = Extension()
        antigen_status_ext.url = self.ANTIGEN_STATUS_URL

        antigen_codeable_concept = self._to_codeable_concept(
            code=antigen_code,
            display=antigen_display,
            coding_system=ImmunizationVisitor.DEFAULT_CODING_SYSTEM,
            coding_version=ImmunizationVisitor.DEFAULT_CODING_VERSION)
        antigen_ext = self._creer_extension(url=self.ANTIGEN_STATUS_ANTIGEN_URL, valueCodeableConcept=antigen_codeable_concept)
        antigen_status_ext.extension = super().add_or_update_extension_to_extensions(extension=antigen_ext, extensions=antigen_status_ext.extension)

        dose_number_ext = self._creer_extension(url=self.ANTIGEN_STATUS_DOSE_NUMER_URL, valueInteger=dose_number)
        antigen_status_ext.extension = super().add_or_update_extension_to_extensions(extension=dose_number_ext, extensions=antigen_status_ext.extension)

        status_codeable_concept = self._to_codeable_concept(
            code = status_code,
            display=status_display,
            coding_system=ImmunizationVisitor.DEFAULT_CODING_SYSTEM,
            coding_version=ImmunizationVisitor.DEFAULT_CODING_VERSION
        )
        status_ext = self._creer_extension(url=self.ANTIGEN_STATUS_STATUS_URL, valueCodeableConcept=status_codeable_concept)
        antigen_status_ext.extension = super().add_or_update_extension_to_extensions(extension=status_ext, extensions=antigen_status_ext.extension)

        self.getFhirResource().extension = super().add_or_update_extension_to_extensions(extension=antigen_status_ext, extensions=self.getFhirResource().extension)

    def get_antigen_status(self) -> Extension:
        if self.getFhirResource().extension is not None:
            for ext in self.getFhirResource().extension:
                if ext.url == self.ANTIGEN_STATUS_URL:
                    return ext
        return None

    def get_antigen_status_antigen(self) -> Coding:
        if self.get_antigen_status() is not None:
            for antigen_extension in self.get_antigen_status().extension:
                if antigen_extension.url == self.ANTIGEN_STATUS_ANTIGEN_URL:
                    return self._get_coding_par_system(codeableConcept=antigen_extension.valueCodeableConcept,
                                                              coding_system=ImmunizationVisitor.DEFAULT_CODING_SYSTEM,
                                                              coding_version=ImmunizationVisitor.DEFAULT_CODING_VERSION)
        return None

    def get_antigen_status_dose_number(self) -> int:
        if self.get_antigen_status() is not None:
            for antigen_extension in self.get_antigen_status().extension:
                if antigen_extension.url == self.ANTIGEN_STATUS_DOSE_NUMER_URL:
                    return antigen_extension.valueInteger
        return None

    def get_antigen_status_status(self) -> Coding:
        if self.get_antigen_status() is not None:
            for antigen_extension in self.get_antigen_status().extension:
                if antigen_extension.url == self.ANTIGEN_STATUS_STATUS_URL:
                    return self._get_coding_par_system(codeableConcept=antigen_extension.valueCodeableConcept,
                                                              coding_system=ImmunizationVisitor.DEFAULT_CODING_SYSTEM,
                                                              coding_version=ImmunizationVisitor.DEFAULT_CODING_VERSION)
        return None

    def get_lot_id(self):
        if self.getFhirResource() is None or self.getFhirResource().extension is None:
            return None
        for extension in self.getFhirResource().extension:
            if extension.url == self.LOT_ID_URL:
                return extension.valueString
        return None
    
    def set_lot_id(self, lot_id=None):
        lot_id_ext = Extension()
        lot_id_ext.url = self.LOT_ID_URL
        lot_id_ext.valueString = lot_id
        self.getFhirResource().extension = super().add_or_update_extension_to_extensions(extension=lot_id_ext, extensions=self.getFhirResource().extension)

    def get_trade_name(self):
        if self.getFhirResource() is None or self.getFhirResource().extension is None:
            return None
        for extension in self.getFhirResource().extension:
            if extension.url == self.TRADE_NAME_URL:
                return extension.valueString
        return None

    def set_trade_name(self, trade_name=None):
        self.getFhirResource().extension = super().add_or_update_extension_to_extensions(extension=self._creer_extension(url=self.TRADE_NAME_URL, valueString=trade_name), 
                                                                                         extensions=self.getFhirResource().extension)
    
    def get_vaccine_code(self) -> Coding:
        vaccine_code = self._get_coding_par_system(
            codeableConcept=self.getFhirResource().vaccineCode)
        return vaccine_code

    def set_vaccine_code(self, vaccine_code:str=None, vaccine_display:str=None):
        self.getFhirResource().vaccineCode = self._to_codeable_concept(
            code=vaccine_code,
            display=vaccine_display)

    def get_patient(self) -> Reference:
        if self.getFhirResource().patient:
            return self.getFhirResource().patient        
        else:
            return None
    
    def set_patient(self, patient: Patient=None, patient_id: str=None):
        self.getFhirResource().patient = Reference()
        self.getFhirResource().patient.reference = patient.id if patient else patient_id

    def get_performer(self) -> Reference:
        if self.getFhirResource().performer is not None:
            return self.getFhirResource().performer
        return None

    def set_performer(self, performer: Practitioner = None, performer_id: str = None):
        self.getFhirResource().performer = Reference()
        self.getFhirResource().performer.reference = performer.id if performer else performer_id
        if performer and performer.name:
            self.getFhirResource().performer.display = performer.name.given[0] + ' ' + performer.name.family[0]

    def get_location(self) -> Reference:
        return self.getFhirResource().location if self.getFhirResource().location else None

    def set_location(self, location:Location=None, location_id: str = None):
        self.getFhirResource().location = Reference()
        self.getFhirResource().location.reference = location.id if location else location_id
        if location:
            self.getFhirResource().location.display = location.name

    def get_lot_number(self) -> str:
        return self.getFhirResource().lotNumber

    def set_lot_number(self, lot_number=None):
        self.getFhirResource().lotNumber = lot_number

    def get_expiration_date(self) -> FHIRDate:
        if self.getFhirResource().expirationDate is not None:
            return self.getFhirResource().expirationDate
        else:
            return None

    def set_expiration_date(self, expiration_date=None):
        if type(expiration_date) is str:
            self.getFhirResource().expirationDate = datetime.strptime(expiration_date, "%Y-%m-%d")
        else:
            self.getFhirResource().expirationDate = expiration_date

    def get_site(self) -> Coding:
        if self.getFhirResource().site is not None:
            coding = self._get_coding_par_system(
                codeableConcept=self.getFhirResource().site)
            return coding
        return None

    def set_site(self, site_code=None, site_display=None):
        self.getFhirResource().site = self._to_codeable_concept(
            code=site_code,
            display=site_display
        )

    def get_route(self) -> Coding:
        if self.getFhirResource().route is not None:
            coding = self._get_coding_par_system(
                codeableConcept=self.getFhirResource().route)
            return coding
        return None

    def set_route(self, route_code=None, route_display=None):
        self.getFhirResource().route = self._to_codeable_concept(
            code=route_code,
            display=route_display
        )

    def get_dose_quantity(self) -> Quantity:
        return self.getFhirResource().doseQuantity
    
    def set_dose_quantity(self, quantity=None, quantity_code=None, quantity_unit=None, quantity_value=None, quantity_system=None):
        if quantity is not None:
            dose_quantity = quantity
        else:
            dose_quantity = Quantity()
            dose_quantity.code = quantity_code
            dose_quantity.system = quantity_system if quantity_system else ImmunizationVisitor.DEFAULT_CODING_SYSTEM
            dose_quantity.unit = quantity_unit
            dose_quantity.value = quantity_value

        self.getFhirResource().doseQuantity = dose_quantity

    def get_reasons(self) -> List[Coding]:
        if self.getFhirResource().explanation is not None and self.getFhirResource().explanation.reason is not None:
            reasons = []
            for reason in self.getFhirResource().explanation.reason:
                if type(reason) is CodeableConcept:
                    reason_coding = self._get_coding_par_system(
                        codeableConcept=reason)
                    reasons.append(reason_coding)
                elif type(reason) is Coding:
                    reasons.append(reason)
            return reasons

    def set_reason(self, reason_code:str=None, reason_display:str=None):
        self.getFhirResource().explanation = ImmunizationExplanation()
        self.getFhirResource().explanation.reason = []
        self.getFhirResource().explanation.reason.append(self._to_codeable_concept(code=reason_code,
                                                                                    display=reason_display))

    def get_date(self) -> FHIRDate:
        return self.getFhirResource().date

    def set_date(self, date_to_set=None):
        if date_to_set is not None:
            if type(date_to_set) is date or type(date_to_set) is datetime:
                date_to_set = datetime.strftime(date_to_set, "%Y-%m-%dT%H:%M:%S")
        self.getFhirResource().date = FHIRDate(jsonval=date_to_set) if date_to_set is not None else None   

    def get_status(self) -> str:
        return self.getFhirResource().status

    def set_status(self, immunization=None, status=None):
        if immunization is None:
            immunization = self.fhir_resource
        if status is not None:
            self.status = status
        immunization.status = self.status

    def get_reason_for_deletion(self) -> CodeableConcept:
        if self.getFhirResource().extension is not None:
            for ext in self.getFhirResource().extension:
                if ext.url == self.REASON_FOR_DELETION_URL:
                    return ext.valueCodeableConcept
        return None

    def get_other_reason_for_deletion(self) -> str:
        if self.getFhirResource().extension is not None:
            for ext in self.getFhirResource().extension:
                if ext.url == self.OTHER_REASON_FOR_DELETION_URL:
                    return ext.valueString
        return ""

    def set_reason_for_deletion(self, reason_code:str=None, other_reason_for_deletion:str=None):
        status_codeable_concept = self._to_codeable_concept(
            code=reason_code,
            coding_system=ImmunizationVisitor.DEFAULT_CODING_SYSTEM,
            coding_version=ImmunizationVisitor.DEFAULT_CODING_VERSION)
        self.getFhirResource().extension =  super().add_or_update_extension_to_extensions(extension=self._creer_extension(self.REASON_FOR_DELETION_URL, valueCodeableConcept=status_codeable_concept), 
                                                                                         extensions=self.getFhirResource().extension)
        if other_reason_for_deletion is not None:
            self.getFhirResource().extension =  super().add_or_update_extension_to_extensions(extension=self._creer_extension(self.OTHER_REASON_FOR_DELETION_URL, valueString=other_reason_for_deletion), 
                                                                                         extensions=self.getFhirResource().extension)

