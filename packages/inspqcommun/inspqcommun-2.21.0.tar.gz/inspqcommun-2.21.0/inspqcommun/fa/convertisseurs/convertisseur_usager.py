from inspqcommun.fa.ressources.usager import Usager
from inspqcommun.fa.convertisseurs.convertisseur_base import ConvertisseurBase
from fhirclient.models.patient import Patient, PatientContact
from fhirclient.models.identifier import Identifier
from fhirclient.models.humanname import HumanName
from fhirclient.models.extension import Extension
from fhirclient.models.address import Address
from fhirclient.models.contactpoint import ContactPoint
from fhirclient.models.fhirdate import FHIRDate
import logging

log = logging.getLogger(__name__)

class ConvertisseurUsager(ConvertisseurBase):

    def __init__(self) -> None:
        self.__convertisseurAdresse = ConvertisseurUsager.ConvertisseurAdresse()
        self.__convertisseurTelephone = ConvertisseurUsager.ConvertisseurTelephone()
        self.__convertisseurContact = ConvertisseurUsager.ConvertisseurContact()

    def fromJson(self, **kwargs):
        return Usager(**kwargs)

    def toFhir(self, usager: Usager) -> Patient:
        log.debug("Usager à convertir: {}".format(usager.as_json()))

        patient = Patient()
        patient.active = True
        
        patient.identifier = []
        if usager.identifiants:
            for identifiant in usager.identifiants:
                patient.identifier.append(self.__convertirIdentifiant(identifiant))
        else:
            patient.identifier.append(self.__convertirIdentifiant(Usager.Identifiant(type='AUCUN', valeur=None)))
        
        if usager.prenom or usager.nom:
            patient.name = [ self.__convertirPrenomNom(usager.prenom, usager.nom) ]
        
        patient.birthDate = FHIRDate(jsonval=usager.dateNaissance) if usager.dateNaissance is not None else None
        patient.gender = usager.sexe

        if usager.adresse:
            patient.address = [ self.__convertisseurAdresse.toFhir(usager.adresse) ]

        if usager.telephone and usager.telephone.numero:
            patient.telecom = [ self.__convertisseurTelephone.toFhir(usager.telephone) ]
        
        if usager.contacts:
            patient.contact = []
            for contact in usager.contacts:
                patient.contact.append(self.__convertisseurContact.toFhir(contact))

        log.debug("Patient obtenu suite à la conversion: {}".format(patient.as_json()))
        return patient

    def __convertirIdentifiant(self, identifiant: Usager.Identifiant) -> Identifier:
        identifier = Identifier()
        identifier.value = identifiant.valeur
        if identifiant.type:
            identifier.system = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary/identifierType?code={}".format(identifiant.type)
        identifier.type = self._convertirEnCodeableConcept(identifiant.type)
        if identifiant.type == 'NAM':
            extension = Extension()
            extension.url = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#patient/healthcardorigin'
            extension.valueCodeableConcept = self._convertirEnCodeableConcept('QC')
            identifier.extension = [ extension ]
        return identifier

    def __convertirPrenomNom(self, prenom: str, nom: str) -> HumanName:
        name = HumanName()
        name.given = [ prenom ]
        name.family = [ nom ]
        return name
    
    class ConvertisseurAdresse(ConvertisseurBase):

        def toFhir(self, adresse: Usager.Adresse) -> Address:
            address = Address()
            address.line = [ adresse.adresse ]
            address.city = adresse.ville
            address.state = adresse.province
            address.country = adresse.pays
            address.postalCode = adresse.codePostal
            return address
        
    class ConvertisseurTelephone(ConvertisseurBase):

        def toFhir(self, telephone: Usager.Telephone) -> ContactPoint:
            telecom = ContactPoint()
            telecom.system = 'phone'
            telecom.value = '+1' + telephone.numero
            if telephone.extension:
                telecom.value = telecom.value + '#' + telephone.extension
            return telecom
        
    class ConvertisseurContact(ConvertisseurBase):

        def toFhir(self, contact: Usager.Contact) -> PatientContact:
            patientContact = PatientContact()
            patientContact.relationship = [ self._convertirEnCodeableConcept(contact.type) ]
            patientContact.name = HumanName()
            patientContact.name.given = [ contact.prenom ]
            patientContact.name.family = [ contact.nom ]
            return patientContact