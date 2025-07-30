from inspqcommun.fa.validateurs.validateur_usager import ValidateurUsager, ValidateurUsagerPourAppariement
from inspqcommun.fa.ressources.acte_vaccinal import ActeVaccinal
from inspqcommun.fa.validateurs.validateur import Validateur
from inspqcommun.fhir.clients.value_set_client import ValueSetClient
from inspqcommun.fhir.clients.medication_client import MedicationClient
from inspqcommun.fhir.clients.practitioner_client import PractitionerClient
from inspqcommun.fhir.clients.location_client import LocationClient
from inspqcommun.fhir.visitors.value_set import ValueSetVisitor
from inspqcommun.fhir.visitors.medication import MedicationVisitor
from typing import List
import logging

log = logging.getLogger(__name__)

class ValidateurActeVaccinal(Validateur):

    USAGER_PRESENT_MESSAGE = "L'usager pour lequel l'acte vaccinal est administré doit être présent"
    AGENT_PRESENT_MESSAGE = "L'agent immunisant de l'acte vaccinal doit être présent"
    ID_LOT_PRESENT_MESSAGE = "L'id du lot doit être présent lors qu'un lot est spécifié"
    NUMERO_LOT_PRESENT_MESSAGE = "Le numéro du lot doit être présent lors qu'un lot est spécifié"
    DATE_ADMINISTRATION_PRESENTE_MESSAGE = "La date d'administration de l'acte vaccinal doit être présente"
    QUANTITE_VALEUR_PRESENTE_MESSAGE = "La quantité administrée doit être présente"
    ID_VACCINATEUR_PRESENT_MESSAGE = "L'id du vaccinateur doit être présent lorsqu'un vaccinateur est défini"
    ID_LIEU_VACCINATION_PRESENT_MESSAGE = "L'id du lieu de vaccination doit être présent lorsqu'un lieu de vaccination est défini"
    AUTEUR_COMMENTAIRE_PRESENT_MESSAGE = "L'auteur du commentaire doit être présent pour chaque commentaire"
    DATE_COMMENTAIRE_PRESENTE_MESSAGE = "La date du comemntaire doit être présente pour chaque commentaire"
    TEXTE_COMMENTAIRE_PRESENT_MESSAGE = "Le texte du commentaire doit être présent pour chaque commentaire"

    NOM_COMMERCIAL_INEXISTANT_MESSAGE = "Le nom commercial {} n'existe pas"
    ID_LOT_INEXISTANT_POUR_NOM_COMMERCIAL_MESSAGE = "L'id du lot {} n'existe pas dans les lots du produit au nom commercial {}"
    NUMERO_LOT_INEXISTANT_POUR_NOM_COMMERCIAL_MESSAGE = "Le numéro du lot {} n'existe pas dans les lots du produit au nom commercial {}"
    AGENT_INEXISTANT_MESSAGE = "L'agent immunisant au code {} n'existe pas"
    UNITE_POSOLOGIQUE_INEXISTANTE_MESSAGE = "L'unité posologique au code {} n'existe pas"
    SITE_ADMINISTRATION_INEXISTANT_MESSAGE = "Le site d'administration au code {} n'existe pas"
    VOIE_ADMINISTRATION_INEXISTANTE_MESSAGE = "La voie d'administration au code {} n'existe pas"
    RAISON_ADMINISTRATION_INEXISTANTE_MESSAGE = "La raison d'administration au code {} n'existe pas"
    VACCINATEUR_INEXISTANT_MESSAGE = "Le vaccinateur qui a l'id {} n'existe pas"
    LIEU_VACCINATION_INEXISTANT_MESSAGE = "Le lieu de vaccination qui a l'id {} n'existe pas"

    def __init__(self, validateur_usager_pour_appariement: ValidateurUsagerPourAppariement, value_set_client: ValueSetClient, 
                 medication_client: MedicationClient, practitioner_client: PractitionerClient, location_client: LocationClient) -> None:
        super().__init__(value_set_client)
        self.__validateur_usager_pour_appariement = validateur_usager_pour_appariement
        self.__medication_client = medication_client
        self.__practitioner_client = practitioner_client
        self.__location_client = location_client

    def valider(self, acte_vaccinal: ActeVaccinal) -> List[str]:
        erreurs: List[str] = []

        erreurs += self.__validateur_usager_pour_appariement.valider(acte_vaccinal.usager)
        erreurs += self.__valider_champs_obligatoires(acte_vaccinal)
        erreurs += self.__valider_domaines_vocabulaire(acte_vaccinal)

        if erreurs:
            log.warn("L'acte vaccinal n'est pas valide", extra={"erreurs":";".join(erreurs)})
        else:
            log.info("L'acte vaccinal a été validé et n'a pas d'erreurs")

        return erreurs
    
    def __valider_champs_obligatoires(self, acte_vaccinal: ActeVaccinal) -> List[str]:
        erreurs: List[str] = []

        if not acte_vaccinal.usager:
            log.debug(self.USAGER_PRESENT_MESSAGE)
            erreurs.append(self.USAGER_PRESENT_MESSAGE)
        
        if not acte_vaccinal.agent:
            log.debug(self.AGENT_PRESENT_MESSAGE)
            erreurs.append(self.AGENT_PRESENT_MESSAGE)
        
        if acte_vaccinal.lot:
            if not acte_vaccinal.lot.id:
                log.debug(self.ID_LOT_PRESENT_MESSAGE)
                erreurs.append(self.ID_LOT_PRESENT_MESSAGE)
            if not acte_vaccinal.lot.numero:
                log.debug(self.NUMERO_LOT_PRESENT_MESSAGE)
                erreurs.append(self.NUMERO_LOT_PRESENT_MESSAGE)
            
        if not acte_vaccinal.dateAdministration:
            log.debug(self.DATE_ADMINISTRATION_PRESENTE_MESSAGE)
            erreurs.append(self.DATE_ADMINISTRATION_PRESENTE_MESSAGE)
        
        if acte_vaccinal.quantiteAdministree:
            if not acte_vaccinal.quantiteAdministree.quantite:
                log.debug(self.QUANTITE_VALEUR_PRESENTE_MESSAGE)
                erreurs.append(self.QUANTITE_VALEUR_PRESENTE_MESSAGE)
        
        if acte_vaccinal.vaccinateur:
            if not acte_vaccinal.vaccinateur.id:
                log.debug(self.ID_VACCINATEUR_PRESENT_MESSAGE)
                erreurs.append(self.ID_VACCINATEUR_PRESENT_MESSAGE)

        if acte_vaccinal.lieuVaccination:
            if not acte_vaccinal.lieuVaccination.id:
                log.debug(self.ID_LIEU_VACCINATION_PRESENT_MESSAGE)
                erreurs.append(self.ID_LIEU_VACCINATION_PRESENT_MESSAGE)

        if acte_vaccinal.commentaires:
            for commentaire in acte_vaccinal.commentaires:
                if not commentaire.auteur:
                    log.debug(self.AUTEUR_COMMENTAIRE_PRESENT_MESSAGE)
                    erreurs.append(self.AUTEUR_COMMENTAIRE_PRESENT_MESSAGE)
                if not commentaire.date:
                    log.debug(self.DATE_COMMENTAIRE_PRESENTE_MESSAGE)
                    erreurs.append(self.DATE_COMMENTAIRE_PRESENTE_MESSAGE)
                if not commentaire.texte:
                    log.debug(self.TEXTE_COMMENTAIRE_PRESENT_MESSAGE)
                    erreurs.append(self.TEXTE_COMMENTAIRE_PRESENT_MESSAGE)
        
        return erreurs
    
    def __valider_domaines_vocabulaire(self, acte_vaccinal: ActeVaccinal) -> List[str]:
        erreurs: List[str] = []

        if acte_vaccinal.usager:
            if acte_vaccinal.usager.identifiants:
                for identifiant in acte_vaccinal.usager.identifiants:
                    if not self._code_present_dans_domaine_vocabulaire(identifiant.type, self._value_set_client.get_identifiertype()):
                        log.debug(ValidateurUsager.TYPE_IDENTIFIANT_INEXISTANT_MESSAGE.format(identifiant.type, identifiant.valeur))
                        erreurs.append(ValidateurUsager.TYPE_IDENTIFIANT_INEXISTANT_MESSAGE.format(identifiant.type, identifiant.valeur))
            if acte_vaccinal.usager.contacts:
                for contact in acte_vaccinal.usager.contacts:
                    if not self._code_present_dans_domaine_vocabulaire(contact.type, self._value_set_client.get_contacttype()):
                        log.debug(ValidateurUsager.TYPE_CONTACT_INEXISTANT_MESSAGE.format(contact.type, contact.prenom, contact.nom))
                        erreurs.append(ValidateurUsager.TYPE_CONTACT_INEXISTANT_MESSAGE.format(contact.type, contact.prenom, contact.nom))
                    
        if acte_vaccinal.nomCommercial:
            response = self.__medication_client.get_by_trade_name(trade_name=acte_vaccinal.nomCommercial)
            if not response.status_code == 200:
                log.debug(self.NOM_COMMERCIAL_INEXISTANT_MESSAGE.format(acte_vaccinal.nomCommercial))
                erreurs.append(self.NOM_COMMERCIAL_INEXISTANT_MESSAGE.format(acte_vaccinal.nomCommercial))
            else:
                if acte_vaccinal.lot:
                    medicationVisitor = MedicationVisitor(self.__medication_client.extract_medication_from_response(medication_response=response))
                    if acte_vaccinal.lot.id and not medicationVisitor.exists_lot_id_in_lots(acte_vaccinal.lot.id):
                        log.debug(self.ID_LOT_INEXISTANT_POUR_NOM_COMMERCIAL_MESSAGE.format(acte_vaccinal.lot.id, acte_vaccinal.nomCommercial))
                        erreurs.append(self.ID_LOT_INEXISTANT_POUR_NOM_COMMERCIAL_MESSAGE.format(acte_vaccinal.lot.id, acte_vaccinal.nomCommercial))
                    if  acte_vaccinal.lot.numero and not medicationVisitor.exists_lot_number_in_lots(acte_vaccinal.lot.numero):
                        log.debug(self.NUMERO_LOT_INEXISTANT_POUR_NOM_COMMERCIAL_MESSAGE.format(acte_vaccinal.lot.numero, acte_vaccinal.nomCommercial))
                        erreurs.append(self.NUMERO_LOT_INEXISTANT_POUR_NOM_COMMERCIAL_MESSAGE.format(acte_vaccinal.lot.numero, acte_vaccinal.nomCommercial))
            
        if acte_vaccinal.agent and not self._code_present_dans_domaine_vocabulaire(acte_vaccinal.agent, self._value_set_client.get_agent()):
            log.debug(self.AGENT_INEXISTANT_MESSAGE.format(acte_vaccinal.agent))
            erreurs.append(self.AGENT_INEXISTANT_MESSAGE.format(acte_vaccinal.agent))
            
        if acte_vaccinal.quantiteAdministree:
            if acte_vaccinal.quantiteAdministree.unite and not self._code_present_dans_domaine_vocabulaire(acte_vaccinal.quantiteAdministree.unite, self._value_set_client.get_dosageunit()):
                log.debug(self.UNITE_POSOLOGIQUE_INEXISTANTE_MESSAGE.format(acte_vaccinal.quantiteAdministree.unite))
                erreurs.append(self.UNITE_POSOLOGIQUE_INEXISTANTE_MESSAGE.format(acte_vaccinal.quantiteAdministree.unite))
        
        if acte_vaccinal.voieAdministration and not self._code_present_dans_domaine_vocabulaire(acte_vaccinal.voieAdministration, self._value_set_client.get_administrationroute()):
            log.debug(self.VOIE_ADMINISTRATION_INEXISTANTE_MESSAGE.format(acte_vaccinal.voieAdministration))
            erreurs.append(self.VOIE_ADMINISTRATION_INEXISTANTE_MESSAGE.format(acte_vaccinal.voieAdministration))
        
        if acte_vaccinal.siteAdministration and not self._code_present_dans_domaine_vocabulaire(acte_vaccinal.siteAdministration, self._value_set_client.get_administrationsite()):
            log.debug(self.SITE_ADMINISTRATION_INEXISTANT_MESSAGE.format(acte_vaccinal.siteAdministration))
            erreurs.append(self.SITE_ADMINISTRATION_INEXISTANT_MESSAGE.format(acte_vaccinal.siteAdministration))
        
        if acte_vaccinal.raisonAdministration and not self._code_present_dans_domaine_vocabulaire(acte_vaccinal.raisonAdministration, self._value_set_client.get_administrationreason()):
            log.debug(self.RAISON_ADMINISTRATION_INEXISTANTE_MESSAGE.format(acte_vaccinal.raisonAdministration))
            erreurs.append(self.RAISON_ADMINISTRATION_INEXISTANTE_MESSAGE.format(acte_vaccinal.raisonAdministration))
        
        if acte_vaccinal.vaccinateur and acte_vaccinal.vaccinateur.id:
            response = self.__practitioner_client.get_by_id(practitioner_id=acte_vaccinal.vaccinateur.id)
            if response.status_code == 404:
                log.debug(self.VACCINATEUR_INEXISTANT_MESSAGE.format(acte_vaccinal.vaccinateur.id))
                erreurs.append(self.VACCINATEUR_INEXISTANT_MESSAGE.format(acte_vaccinal.vaccinateur.id))
        
        if acte_vaccinal.lieuVaccination and acte_vaccinal.lieuVaccination.id:
            response = self.__location_client.get_by_id(location_id=acte_vaccinal.lieuVaccination.id)
            if response.status_code == 404:
                log.debug(self.LIEU_VACCINATION_INEXISTANT_MESSAGE.format(acte_vaccinal.lieuVaccination.id))
                erreurs.append(self.LIEU_VACCINATION_INEXISTANT_MESSAGE.format(acte_vaccinal.lieuVaccination.id))
        
        return erreurs