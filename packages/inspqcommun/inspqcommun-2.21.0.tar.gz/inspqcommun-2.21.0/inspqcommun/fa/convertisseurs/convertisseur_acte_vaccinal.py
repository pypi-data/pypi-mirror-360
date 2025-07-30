from inspqcommun.fa.ressources.usager import Usager
from inspqcommun.fa.ressources.acte_vaccinal import ActeVaccinal
from inspqcommun.fhir.clients.patient_client import PatientClient
from inspqcommun.fa.convertisseurs.convertisseur_usager import ConvertisseurUsager
from inspqcommun.fa.convertisseurs.convertisseur_base import ConvertisseurBase

from fhirclient.models.extension import Extension
from fhirclient.models.immunization import Immunization, ImmunizationExplanation
from fhirclient.models.quantity import Quantity
from fhirclient.models.reference import Reference
from fhirclient.models.annotation import Annotation

import logging

log = logging.getLogger(__name__)

class ConvertisseurActeVaccinal(ConvertisseurBase):

    def __init__(self, convertisseur_usager: ConvertisseurUsager, patient_client: PatientClient) -> None:
        self.__convertisseur_usager : ConvertisseurUsager = convertisseur_usager
        self.__patient_client: PatientClient = patient_client

    def fromJson(self, **kwargs):
        return ActeVaccinal(**kwargs)

    def toFhir(self, acte_vaccinal: ActeVaccinal) -> Immunization:
        log.debug("Acte vaccinal à convertir: {}".format(acte_vaccinal.as_json()))

        immunization = Immunization()

        immunization.status = 'completed'
        immunization.wasNotGiven = False

        immunization.patient = self.__obtenir_reference_usager_par_appariement(acte_vaccinal.usager)

        immunization.extension = []

        if acte_vaccinal.nomCommercial:
            tradename = Extension()
            tradename.url = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/tradename'
            tradename.valueString = acte_vaccinal.nomCommercial
            immunization.extension.append(tradename)

            if acte_vaccinal.lot:
                lotId = Extension()
                lotId.url = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/lotid'
                lotId.valueString = acte_vaccinal.lot.id
                immunization.extension.append(lotId)
                immunization.lotNumber = acte_vaccinal.lot.numero
        
        if acte_vaccinal.agent:
            immunization.vaccineCode = self._convertirEnCodeableConcept(acte_vaccinal.agent)

        immunization.date = acte_vaccinal.dateAdministration
        
        if acte_vaccinal.quantiteAdministree:
            immunization.doseQuantity = Quantity()
            immunization.doseQuantity.value = acte_vaccinal.quantiteAdministree.quantite
            immunization.doseQuantity.code = acte_vaccinal.quantiteAdministree.unite if acte_vaccinal.quantiteAdministree.unite else 'I'
            immunization.doseQuantity.system = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary'

        immunization.route = self._convertirEnCodeableConcept(acte_vaccinal.voieAdministration) if acte_vaccinal.voieAdministration else self._convertirEnCodeableConcept('UNKN')
        immunization.site = self._convertirEnCodeableConcept(acte_vaccinal.siteAdministration) if acte_vaccinal.siteAdministration else self._convertirEnCodeableConcept('I')

        if acte_vaccinal.raisonAdministration:
            explanation = ImmunizationExplanation()
            explanation.reason = [ self._convertirEnCodeableConcept(acte_vaccinal.raisonAdministration) ]
            immunization.explanation = explanation

        immunization.performer = Reference()
        immunization.performer.reference = str(acte_vaccinal.vaccinateur.id) if acte_vaccinal.vaccinateur else '20497'

        immunization.location = Reference()
        immunization.location.reference = str(acte_vaccinal.lieuVaccination.id) if acte_vaccinal.lieuVaccination else '6906'

        if acte_vaccinal.commentaires:
            immunization.note = []
            for commentaire in acte_vaccinal.commentaires:
                note = Annotation()
                note.authorString = commentaire.auteur
                note.time = commentaire.date
                note.text = commentaire.texte
                immunization.note.append(note)

        immunization.reported = not acte_vaccinal.nomCommercial or not acte_vaccinal.quantiteAdministree

        log.debug("Immunization obtenue suite à la conversion: {}".format(immunization.as_json()))
        return immunization
    
    def __obtenir_reference_usager_par_appariement(self, usager: Usager) -> Reference:
        patient = self.__convertisseur_usager.toFhir(usager)
        response = self.__patient_client.match(patient)
        if response.status_code == 200:
            patient = self.__patient_client.extract_patient_from_response(response)
            log.debug("Patient reçu pour l'ajout d'un acte vaccinal suite à un appariement: {}".format(patient.as_json()))
            reference = Reference()
            reference.reference = str(patient.id)
            return reference
        else:
            return None