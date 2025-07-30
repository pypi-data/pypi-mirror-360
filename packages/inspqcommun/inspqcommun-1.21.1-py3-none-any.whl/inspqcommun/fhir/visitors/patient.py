from fhirclient.models.patient import Patient, PatientContact
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.extension import Extension
from fhirclient.models.identifier import Identifier
from fhirclient.models.humanname import HumanName
from fhirclient.models.address import Address
from fhirclient.models.contactpoint import ContactPoint

from inspqcommun.fhir.visitors.base import BaseVisitor

class PatientVisitor(BaseVisitor):
    
    NAM_IDENTIFIER_EXTENSION_URL = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#patient/healthcardorigin"
    NAM_IDENTIFIER_SYSTEM = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary/identifierType?code=NAM"
    NIU_IDENTIFIER_SYSTEM = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary/identifierType?code=NIUU"
    AUCUN_IDENTIFIER_SYSTEM = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary/identifierType?code=AUCUN"
    MATCHRAMQ_EXTENSION_URL = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#patient/matchramq"

    def __init__(self, fhir_resource: Patient=None):
        self.setFhirResource(fhir_resource=fhir_resource if fhir_resource else Patient())

    def __contains__(self, value: object) -> bool:
        contained = self._is_struct_included(value.getFhirResource().as_json(), self.getFhirResource().as_json(), exclude=['identifier'])
        if contained:
            niu_equal = True
            if self.get_niu() is not None and value.get_niu() is not None:
                niu_equal = self.get_niu().value == value.get_niu().value
            nam_equal = True
            if value.get_nam() is not None:
                nam_equal = self.get_nam().value == value.get_nam().value
            return niu_equal and nam_equal
        return contained

    def getFhirResource(self) -> Patient:
        return super().getFhirResource() 

    def set_id(self, id):
        self.getFhirResource().id = id

    def get_id(self, patient=None):
        if patient is None:
            patient = self.getFhirResource()
        return patient.id

    def get_matchramq(self) -> bool:
        if self.getFhirResource() and self.getFhirResource().extension:
            matchRamq = self.__trouver_extension_par_url(url=self.MATCHRAMQ_EXTENSION_URL, extensions=self.getFhirResource().extension)
            if matchRamq:
                return matchRamq.valueBoolean
        return False

    def set_active(self, active: bool):
        self.getFhirResource().active = active

    def get_active(self):
        return self.getFhirResource().active

    def set_name(self, given_name=None, family_name=None):
        if not given_name and not family_name:
            self.getFhirResource().name = None
        else:
            if not self.getFhirResource().name:
                self.getFhirResource().name = []
                name = HumanName()
                name.given = [given_name] if given_name else None
                name.family = [family_name] if family_name else None
                self.getFhirResource().name.append(name)

    def get_given_name(self, index=0):
        return self.getFhirResource().name[index].given[0] if self.getFhirResource().name[index] and self.getFhirResource().name[index].given else None

    def get_family_name(self, index=0):
        return self.getFhirResource().name[index].family[0] if self.getFhirResource().name and self.getFhirResource().name[index].family else None

    def set_gender(self, gender: str):
        self.getFhirResource().gender = gender

    def get_gender(self):
        return self.getFhirResource().gender

    def set_nam(self, nam:str=None):
        self.__definir_identifiant_par_system(valeur=nam, code='NAM', system=self.NAM_IDENTIFIER_SYSTEM)

    def get_nam(self) -> Identifier:
        if self.getFhirResource() and self.getFhirResource().identifier:
            for identifier in self.getFhirResource().identifier:
                if identifier.system == self.NAM_IDENTIFIER_SYSTEM:
                    return identifier
        return None

    def set_niu(self, niu:str=None):
        self.__definir_identifiant_par_system(valeur=niu, code='NIUU', system=self.NIU_IDENTIFIER_SYSTEM)
        if not self.getFhirResource().extension:
            self.getFhirResource().extension = []
        matchRamq = self.__trouver_extension_par_url(url=self.MATCHRAMQ_EXTENSION_URL, extensions=self.getFhirResource().extension)
        if matchRamq:
            matchRamq.valueBoolean = niu is not None
        else:
            matchRamq = Extension()
            matchRamq.url = self.MATCHRAMQ_EXTENSION_URL
            matchRamq.valueBoolean = niu is not None
            self.getFhirResource().extension.append(matchRamq)

    def __trouver_extension_par_url(self, url: str, extensions) -> Extension:
        if extensions:
            for extension in extensions:
                if extension.url == url:
                    return extension
        return None

    def get_niu(self) -> Identifier:
        if self.getFhirResource() and self.getFhirResource().identifier:
            for identifier in self.getFhirResource().identifier:
                if identifier.system == self.NIU_IDENTIFIER_SYSTEM:
                    return identifier
        return None

    def set_aucun_identifiant(self):
        self.set_nam()
        self.set_niu()
        self.__definir_identifiant_par_system(code='AUCUN', system=self.AUCUN_IDENTIFIER_SYSTEM)

    def set_birth_date(self, birth_date: str):
        self.getFhirResource().birthDate = self.str_date_to_fhir_date(birth_date)

    def get_birth_date(self):
        return self.fhir_date_to_str_date(fhir_date=self.getFhirResource().birthDate)

    def set_address(self, address_line=None, address_city=None, address_state=None, address_postal_code=None, address_country=None):
        if not address_line and not address_city and not address_state and not address_country and not address_postal_code:
            self.getFhirResource().address = None
        else:
            address = Address()
            address.city = address_city
            address.country = address_country
            address.state = address_state
            address.postalCode = address_postal_code
            address.line = [address_line]
            self.getFhirResource().address = [address]

    def get_address(self) -> Address:
        if self.getFhirResource() and self.getFhirResource().address:
            return self.getFhirResource().address[0]
        else:
            return None

    def set_mother_name(self, mother_given_name=None, mother_family_name=None):
        self.__definir_contact_par_type(type='MERE', given_name=mother_given_name, family_name=mother_family_name)

    def get_mother_name(self) -> HumanName:
        if self.getFhirResource() and self.getFhirResource().contact:
            for contact in self.getFhirResource().contact:
                for relationship in contact.relationship:
                    for coding in relationship.coding:
                        if coding.code == 'MERE' and coding.system == PatientVisitor.DEFAULT_CODING_SYSTEM and coding.version == PatientVisitor.DEFAULT_CODING_VERSION:
                            return contact.name
        return None
        
    def set_father_name(self, father_given_name=None, father_family_name=None):
        self.__definir_contact_par_type(type='PERE', given_name=father_given_name, family_name=father_family_name)
        
    def get_father_name(self):
        if self.getFhirResource() and self.getFhirResource().contact:
            for contact in self.getFhirResource().contact:
                for relationship in contact.relationship:
                    for coding in relationship.coding:
                        if coding.code == 'PERE' and coding.system == PatientVisitor.DEFAULT_CODING_SYSTEM and coding.version == PatientVisitor.DEFAULT_CODING_VERSION:
                            return contact.name
        return None

    def set_phone_number(self, phone_number: str=None):
        if phone_number:
            self.getFhirResource().telecom = []
            telecom = ContactPoint()
            telecom.system = 'phone'
            telecom.value = phone_number
            self.getFhirResource().telecom.append(telecom)
        else:
            self.getFhirResource().telecom = None
         
    def get_phone_number(self) -> str:
        if self.getFhirResource() and self.getFhirResource().telecom:
            for telecom in self.getFhirResource().telecom:
                if telecom.system == 'phone':
                    return telecom.value
        return None
    
    def set_date_of_death(self, date_of_death: str):
        self.getFhirResource().deceasedDateTime = self.str_date_to_fhir_date(date_of_death)

    def get_date_of_death(self):
        return self.fhir_date_to_str_date(fhir_date=self.getFhirResource().deceasedDateTime)

    def __definir_identifiant_par_system(self, code: str, system:str, valeur:str=None):

        if self.getFhirResource().identifier:
            identifier_existant = None
            for identifier in self.getFhirResource().identifier:
                if identifier.system == system:
                    identifier_existant=identifier
        
            if identifier_existant:
                self.getFhirResource().identifier.remove(identifier_existant)
        
        if valeur or system == self.AUCUN_IDENTIFIER_SYSTEM:
            if not self.getFhirResource().identifier:
                self.getFhirResource().identifier = []
            
            self.getFhirResource().identifier.append(self.__creer_identifier(code=code, valeur=valeur, system=system, coding_system=self.DEFAULT_CODING_SYSTEM, coding_version=self.DEFAULT_CODING_VERSION))
    
    def __creer_identifier(self, code: str, system: str, coding_system, coding_version, valeur:str=None):
        identifier = Identifier()

        if (system == self.NAM_IDENTIFIER_SYSTEM):
            healthcardorigin = Extension()
            healthcardorigin.url = self.NAM_IDENTIFIER_EXTENSION_URL
            healthcardorigin.valueCodeableConcept = self._to_codeable_concept(code='QC', coding_system=coding_system, coding_version=coding_version)
            identifier.extension = [healthcardorigin]

        identifier.type = self._to_codeable_concept(code=code, coding_system=coding_system, coding_version=coding_version)
        identifier.system = system
        identifier.value = valeur
        
        return identifier
    
    def __definir_contact_par_type(self, type:str, given_name:str=None, family_name:str=None):
        if not self.getFhirResource().contact:
            self.getFhirResource().contact = []

        contact: PatientContact
        relationship: CodeableConcept
        contact_existant: PatientContact = None

        for contact in self.getFhirResource().contact:
            for relationship in contact.relationship:
                if self._get_coding_par_system(relationship).code == type:
                    contact_existant = contact
        
        if contact_existant:
            self.getFhirResource().contact.remove(contact_existant)
        
        if given_name and family_name:
            self.getFhirResource().contact.append(self.__creer_contact(given_name=given_name, family_name=family_name, type=type))
    
    def __creer_contact(self, given_name:str, family_name:str, type:str) -> PatientContact:
        contact = PatientContact()
        contact.relationship = [ self._to_codeable_concept(code=type) ]
        contact.name = HumanName()
        contact.name.given = [given_name]
        contact.name.family = [family_name]
        return contact