from fhirclient.models.location import Location
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models.period import Period
from fhirclient.models.extension import Extension
from fhirclient.models.identifier import Identifier
from fhirclient.models.address import Address
from fhirclient.models.reference import Reference
from fhirclient.models.contactpoint import ContactPoint
from inspqcommun.fhir.visitors.base import BaseVisitor

class LocationVisitor(BaseVisitor):
    
    RRSS_SYSTEM = 'https://pro.consultation.rrss.rtss.qc.ca'
    RRSS_MOT_CLE_EXTENSION_URL = 'http://www.santepublique.rtss.qc.ca/sipmi/rrss/1.0.0/extensions/#motscles'
    PERIOD_URL = "http://www.santepublique.rtss.qc.ca/sipmi/rrss/1.0.0/extensions/period"

    def __init__(self, fhir_resource=None) -> None:
        self.setFhirResource(fhir_resource=fhir_resource if fhir_resource else Location())

    def getFhirResource(self) -> Location:
        return super().getFhirResource()        

    def have_mot_cle(self, mot_cle=None):
        if mot_cle is not None and self.getFhirResource().extension is not None:
            for extension in self.getFhirResource().extension:
                if extension.url == self.RRSS_MOT_CLE_EXTENSION_URL and extension.valueString == mot_cle:
                    return True
        return False

    def set_name(self, name=None):
        self.getFhirResource().name = name

    def get_name(self):
        return self.getFhirResource().name

    def get_id(self):
        return self.getFhirResource().id

    def get_id_rrss(self):
        if self.getFhirResource().identifier is not None:
            for identifier in self.getFhirResource().identifier:
                if identifier.system == self.RRSS_SYSTEM:
                    return identifier.value
        return None

    def get_address_city(self):
        if self.getFhirResource().address:
            return self.getFhirResource().address.city
        return None

    def get_phones(self):
        phones = []
        if self.getFhirResource().telecom is None:
            return phones
        for telecom in self.getFhirResource().telecom:
            if telecom.system == "phone":
                phone = {}
                phone["value"] = telecom.value
                phone["use"] = telecom.use
                phones.append(phone)
        return phones
    
    def set_phones(self, phones:list[dict]=None):
        if phones is not None:
            telecoms = []
            for phone in phones:
                telecom = ContactPoint()

                telecom.system = phone["system"] if "system" in phone else "phone"
                telecom.value = phone["value"]
                telecom.use = phone["use"] if "use" in phone else "work"

                telecoms.append(telecom)
            self.getFhirResource().telecom = telecoms

    def get_effective_from(self):
        period_ext = self.__get_period_ext()
        if period_ext is not None and period_ext.valuePeriod is not None:
                return period_ext.valuePeriod.start
        return None

    def get_effective_to(self):
        period_ext = self.__get_period_ext()
        if period_ext is not None and period_ext.valuePeriod is not None:
                return period_ext.valuePeriod.end
        return None

    def set_effective_from(self, effective_from=None):
        fhir_effective_from = None
        if type(effective_from) is str:
            fhir_effective_from = FHIRDate(jsonval=effective_from)
        elif type(effective_from) is FHIRDate:
            fhir_effective_from = effective_from
        period_ext = self.__get_period_ext()
        if period_ext is None or period_ext.valuePeriod is None:
            period = Period()
        else:
            period = period_ext.valuePeriod
        period.start = fhir_effective_from
        self.__set_period_ext(period=period)

    def set_effective_to(self, effective_to=None):
        fhir_effective_to = None
        if type(effective_to) is str:
            fhir_effective_to = FHIRDate(jsonval=effective_to)
        elif type(effective_to) is FHIRDate:
            fhir_effective_to = effective_to
        period_ext = self.__get_period_ext()
        if period_ext is None or period_ext.valuePeriod is None:
            period = Period()
        else:
            period = period_ext.valuePeriod
        period.end = fhir_effective_to
        self.__set_period_ext(period=period)

    def is_active(self):
        return self.getFhirResource().status == "active"
    
    def __get_period_ext(self):
        if self.getFhirResource().extension is not None:
            for ext in self.getFhirResource().extension:
                if ext.url == self.PERIOD_URL:
                    return ext
        return None

    def __set_period_ext(self, period=None):
        if self.getFhirResource().extension is None:
            self.getFhirResource().extension = []
        period_ext = self.__get_period_ext()
        if period_ext is None:
            period_ext = Extension()
            period_ext.url = self.PERIOD_URL
            self.getFhirResource().extension.append(period_ext)
        period_ext.valuePeriod = period
        
    def set_id_rrss(self, id_rrss=None):
        if id_rrss is not None:
            identifier = Identifier()
            identifier.system = self.RRSS_SYSTEM
            identifier.value = id_rrss
            if self.get_id_rrss() is None:
                self.getFhirResource().identifier = []
                self.getFhirResource().identifier.append(identifier)
            else:
                for idx, id in enumerate(self.getFhirResource().identifier):
                    if id.system == self.RRSS_SYSTEM:
                        self.getFhirResource().identifier[idx] = identifier
                        break

    def set_address(self, address: Address=None, city: str=None, postal_code:str=None, country:str=None, state:str=None, line:str=None):
        if address is not None:
            self.getFhirResource().address = address
        else:
            if self.getFhirResource().address is None:
                self.getFhirResource().address = Address()
            self.getFhirResource().address.city = city
            if postal_code is not None:
                self.getFhirResource().address.postalCode = postal_code
            if country is not None:
                self.getFhirResource().address.country = country
            if state is not None:
                self.getFhirResource().address.state = state
            if line is not None:
                self.getFhirResource().address.line = [line]

    def get_address(self) -> Address:
        return self.getFhirResource().address
    
    def get_managing_organization(self) -> Reference:
        if self.getFhirResource().managingOrganization is not None:
            return self.getFhirResource().managingOrganization.reference
        return None

    def set_managing_organization(self, managing_organization:str=None):
        if managing_organization is not None:
            reference = Reference()
            reference.reference = managing_organization
            self.getFhirResource().managingOrganization = reference

    def get_description(self) -> str:
        return self.getFhirResource().description

    def set_description(self, description: str=None):
        self.getFhirResource().description = description