from inspqcommun.fa.ressources.usager import Usager
from inspqcommun.fhir.clients.value_set_client import ValueSetClient
from inspqcommun.fa.validateurs.validateur import Validateur
from typing import List
import logging

log = logging.getLogger(__name__)

class ValidateurUsager(Validateur):
    TYPE_IDENTIFIANT_POUR_NIU = "NIUU"
    PRENOM_USAGER_PRESENT_MESSAGE = "Le prénom de l'usager doit être présent"
    NOM_USAGER_PRESENT_MESSAGE = "Le nom de l'usager doit être présent"
    DATE_NAISSANCE_USAGER_PRESENTE_MESSAGE = "La date de naissance de l'usager doit être présente"
    SEXE_USAGER_PRESENT_MESSAGE = "Le sexe de l'usager doit être présent"
    IDENTIFIANTS_OU_CONTACTS_USAGER_PRESENT_MESSAGE = "L'usager doit avoir au moins un identifiant ou un contact"
    TYPE_ET_VALEUR_IDENTIFIANTS_USAGER_PRESENTS_MESSAGE = "Tous les identifiants doivent avoir un type et une valeur"
    TYPE_ET_PRENOM_ET_NOM_CONTACTS_USAGER_PRESENTS_MESSAGE = "Tous les contacts doivent avoir un type, un prénom et un nom"

    TYPE_IDENTIFIANT_INEXISTANT_MESSAGE = "Le type d'identifiant {} pour l'identifiant {} n'est pas un type d'identifiant qui existe"
    SEXE_INEXISTANT_MESSAGE = "Le sexe {} n'est pas un sexe qui existe"
    VILLE_INEXISTANTE_MESSAGE = "La ville {} n'est pas une ville qui existe"
    PROVINCE_INEXISTANTE_MESSAGE = "La province {} n'est pas une province qui existe"
    PAYS_INEXISTANT_MESSAGE = "Le pays {} n'est pas un pays qui existe"
    TYPE_CONTACT_INEXISTANT_MESSAGE = "Le type de contact {} pour le contact {} {} n'est pas un type de contact qui existe"

    def __init__(self, value_set_client: ValueSetClient) -> None:
        super().__init__(value_set_client)

    def valider(self, usager: Usager) -> List[str]:
        erreurs: List[str] = []
        
        erreurs += self.__valider_champs_obligatoires(usager)
        erreurs += self.__valider_domaines_vocabulaire(usager)
        
        return erreurs

    def __valider_champs_obligatoires(self, usager: Usager) -> List[str]:
        erreurs: List[str] = []
        if not usager.prenom:
            log.debug(self.PRENOM_USAGER_PRESENT_MESSAGE)
            erreurs.append(self.PRENOM_USAGER_PRESENT_MESSAGE)
        if not usager.nom:
            log.debug(self.NOM_USAGER_PRESENT_MESSAGE)
            erreurs.append(self.NOM_USAGER_PRESENT_MESSAGE)
        if not usager.dateNaissance:
            log.debug(self.DATE_NAISSANCE_USAGER_PRESENTE_MESSAGE)
            erreurs.append(self.DATE_NAISSANCE_USAGER_PRESENTE_MESSAGE)
        if not usager.sexe:
            log.debug(self.SEXE_USAGER_PRESENT_MESSAGE)
            erreurs.append(self.SEXE_USAGER_PRESENT_MESSAGE)
        if not usager.identifiants and not usager.contacts:
            log.debug(self.IDENTIFIANTS_OU_CONTACTS_USAGER_PRESENT_MESSAGE)
            erreurs.append(self.IDENTIFIANTS_OU_CONTACTS_USAGER_PRESENT_MESSAGE)
        else:
            erreurs += self.__valider_champs_obligatoires_identifiants(usager.identifiants)
            erreurs += self.__valider_champs_obligatoires_contacts(usager.contacts)
        
        if erreurs:
            log.warn("L'usager n'est pas valide", extra={"erreurs":";".join(erreurs)})
        else:
            log.info("L'usager a été validé et n'a pas d'erreurs")

        return erreurs
    
    def __valider_champs_obligatoires_identifiants(self, identifiants: List[Usager.Identifiant]) -> List[str]:
        erreurs: List[str] = []
        
        if identifiants:
            for identifiant in identifiants:
                if not identifiant.type or not identifiant.valeur:
                    log.debug(self.TYPE_ET_VALEUR_IDENTIFIANTS_USAGER_PRESENTS_MESSAGE)
                    erreurs.append(self.TYPE_ET_VALEUR_IDENTIFIANTS_USAGER_PRESENTS_MESSAGE)
        
        return erreurs
    
    def __valider_champs_obligatoires_contacts(self, contacts: List[Usager.Contact]) -> List[str]:
        erreurs: List[str] = []
        
        if contacts:
            for contact in contacts:
                if not contact.type or not contact.prenom or not contact.nom:
                    log.debug(self.TYPE_ET_PRENOM_ET_NOM_CONTACTS_USAGER_PRESENTS_MESSAGE)
                    erreurs.append(self.TYPE_ET_PRENOM_ET_NOM_CONTACTS_USAGER_PRESENTS_MESSAGE)
        
        return erreurs

    def __valider_domaines_vocabulaire(self, usager: Usager) -> List[str]:
        erreurs: List[str] = []

        if usager.identifiants:
            for identifiant in usager.identifiants:
                if not (identifiant.type == self.TYPE_IDENTIFIANT_POUR_NIU or self._code_present_dans_domaine_vocabulaire(identifiant.type, self._value_set_client.get_identifiertype())):
                    log.debug(self.TYPE_IDENTIFIANT_INEXISTANT_MESSAGE.format(identifiant.type, identifiant.valeur))
                    erreurs.append(self.TYPE_IDENTIFIANT_INEXISTANT_MESSAGE.format(identifiant.type, identifiant.valeur))
                
        if usager.sexe and not self._code_present_dans_domaine_vocabulaire(usager.sexe, self._value_set_client.get_gender()):
            log.debug(self.SEXE_INEXISTANT_MESSAGE.format(usager.sexe))
            erreurs.append(self.SEXE_INEXISTANT_MESSAGE.format(usager.sexe))
        
        if usager.adresse:
            if usager.adresse.ville and not self._description_presente_dans_domaine_vocabulaire(usager.adresse.ville, self._value_set_client.get_city_by_name(name=usager.adresse.ville, province_code=usager.adresse.get_province_code())):
                log.debug(self.VILLE_INEXISTANTE_MESSAGE.format(usager.adresse.ville))
                erreurs.append(self.VILLE_INEXISTANTE_MESSAGE.format(usager.adresse.ville))
            if usager.adresse.province and not self._description_presente_dans_domaine_vocabulaire(usager.adresse.province, self._value_set_client.get_provinces()):
                log.debug(self.PROVINCE_INEXISTANTE_MESSAGE. format(usager.adresse.province))
                erreurs.append(self.PROVINCE_INEXISTANTE_MESSAGE. format(usager.adresse.province))
            if usager.adresse.pays and not self._description_presente_dans_domaine_vocabulaire(usager.adresse.pays, self._value_set_client.get_country()):
                log.debug(self.PAYS_INEXISTANT_MESSAGE.format(usager.adresse.pays))
                erreurs.append(self.PAYS_INEXISTANT_MESSAGE.format(usager.adresse.pays))
            
        if usager.contacts:
            for contact in usager.contacts:
                if not self._code_present_dans_domaine_vocabulaire(contact.type, self._value_set_client.get_contacttype()):
                    log.debug(self.TYPE_CONTACT_INEXISTANT_MESSAGE.format(contact.type, contact.prenom, contact.nom))
                    erreurs.append(self.TYPE_CONTACT_INEXISTANT_MESSAGE.format(contact.type, contact.prenom, contact.nom))
        
        return erreurs

class ValidateurUsagerPourAppariement:

    DATE_NAISSANCE_PRESENTE_MESSAGE = "L'usager doit avoir une date de naissance s'il n'a pas d'identifiants"
    SEXE_PRESENT_MESSAGE = "L'usager doit avoir un sexe s'il n'a pas d'identifiants"
    CONTACTS_PRESENT_MESSAGE = "L'usager doit avoir des contacts s'il n'a pas d'identifiants"

    def valider(self, usager: Usager) -> List[str]:
        erreurs: List[str] = []

        if not usager.identifiants:
            if not usager.prenom:
                log.debug(ValidateurUsager.PRENOM_USAGER_PRESENT_MESSAGE)
                erreurs.append(ValidateurUsager.PRENOM_USAGER_PRESENT_MESSAGE)
            if not usager.nom:
                log.debug(ValidateurUsager.NOM_USAGER_PRESENT_MESSAGE)
                erreurs.append(ValidateurUsager.NOM_USAGER_PRESENT_MESSAGE)
            if not usager.dateNaissance:
                log.debug(self.DATE_NAISSANCE_PRESENTE_MESSAGE)
                erreurs.append(self.DATE_NAISSANCE_PRESENTE_MESSAGE)
            if not usager.sexe:
                log.debug(self.SEXE_PRESENT_MESSAGE)
                erreurs.append(self.SEXE_PRESENT_MESSAGE)
            if not usager.contacts:
                log.debug(self.CONTACTS_PRESENT_MESSAGE)
                erreurs.append(self.CONTACTS_PRESENT_MESSAGE)
            else:
                erreurs += self.__valider_champs_obligatoires_contacts(usager.contacts)
        else:
            if not usager.prenom:
                log.debug(ValidateurUsager.PRENOM_USAGER_PRESENT_MESSAGE)
                erreurs.append(ValidateurUsager.PRENOM_USAGER_PRESENT_MESSAGE)
            if not usager.nom:
                log.debug(ValidateurUsager.NOM_USAGER_PRESENT_MESSAGE)
                erreurs.append(ValidateurUsager.NOM_USAGER_PRESENT_MESSAGE)
        
        return erreurs
    
    def __valider_champs_obligatoires_contacts(self, contacts) -> List[str]:
        erreurs: List[str] = []

        for contact in contacts:
            if not contact.type or not contact.prenom or not contact.nom:
                log.debug(ValidateurUsager.TYPE_ET_PRENOM_ET_NOM_CONTACTS_USAGER_PRESENTS_MESSAGE)
                erreurs.append(ValidateurUsager.TYPE_ET_PRENOM_ET_NOM_CONTACTS_USAGER_PRESENTS_MESSAGE)
        
        return erreurs