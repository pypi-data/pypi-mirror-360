from inspqcommun.fa.configuration import Configuration
from inspqcommun.fhir.clients.base_client import BaseClient
from inspqcommun.fhir.clients.patient_client import PatientClient
from inspqcommun.fhir.clients.immunization_client import ImmunizationClient
from inspqcommun.fhir.clients.value_set_client import ValueSetClient
from inspqcommun.fhir.clients.medication_client import MedicationClient
from inspqcommun.fhir.clients.practitioner_client import PractitionerClient
from inspqcommun.fhir.clients.location_client import LocationClient
from inspqcommun.fhir.clients.organization_client import OrganizationClient
from inspqcommun.fhir.clients.condition_client import ConditionClient
from inspqcommun.fhir.clients.flag_client import FlagClient
from inspqcommun.fa.validateurs.validateur_usager import ValidateurUsager, ValidateurUsagerPourAppariement
from inspqcommun.fa.validateurs.validateur_acte_vaccinal import ValidateurActeVaccinal
from inspqcommun.fa.convertisseurs.convertisseur_usager import ConvertisseurUsager
from inspqcommun.fa.convertisseurs.convertisseur_acte_vaccinal import ConvertisseurActeVaccinal
from inspqcommun.fa.chargeur_fichiers import ChargeurFichiers
from inspqcommun.fa.chargement_service import ChargementService
class Injecteur:

    def __init__(self, configuration: Configuration) -> None:
        self.configuration: Configuration = configuration
        self.base_client: BaseClient = None
        self.patient_client: PatientClient = None
        self.immunization_client: ImmunizationClient = None
        self.value_set_client: ValueSetClient = None
        self.medication_client: MedicationClient = None
        self.practitioner_client: PractitionerClient = None
        self.location_client: LocationClient = None
        self.organization_client: OrganizationClient = None
        self.condition_client: ConditionClient = None
        self.flag_client: FlagClient = None
        self.validateur_usager: ValidateurUsager = None
        self.validateur_usager_pour_appariement: ValidateurUsagerPourAppariement = None
        self.validateur_acte_vaccinal: ValidateurActeVaccinal = None
        self.convertisseur_usager: ConvertisseurUsager = None
        self.convertisseur_acte_vaccinal: ConvertisseurActeVaccinal = None
        self.chargeur_fichiers: ChargeurFichiers = None
        self.chargement_service: ChargementService = None

    def get_base_client(self) -> BaseClient:
        if not self.base_client:
            self.base_client = BaseClient(base_url=self.configuration.get_fonctions_allegees_url(),
                                          base_uri=self.configuration.get_fonctions_allegees_uri(),
                                          token_header=self.__build_headers(),
                                          validate_certs=False)
        return self.base_client

    def get_patient_client(self) -> PatientClient:
        if not self.patient_client:
            self.patient_client = PatientClient(base_url=self.configuration.get_fonctions_allegees_url(), 
                                                base_uri=self.configuration.get_fonctions_allegees_uri(), 
                                                token_header=self.__build_headers(),
                                                validate_certs=False)
        return self.patient_client
    
    def get_immunization_client(self) -> ImmunizationClient:
        if not self.immunization_client:
            self.immunization_client = ImmunizationClient(base_url=self.configuration.get_fonctions_allegees_url(), 
                                                          base_uri=self.configuration.get_fonctions_allegees_uri(), 
                                                          token_header=self.__build_headers(),
                                                          validate_certs=False)
        return self.immunization_client
    
    def get_value_set_client(self) -> ValueSetClient:
        if not self.value_set_client:
            self.value_set_client = ValueSetClient(base_url=self.configuration.get_fonctions_allegees_url(), 
                                                   base_uri=self.configuration.get_fonctions_allegees_uri(), 
                                                   token_header=self.__build_headers(),
                                                   validate_certs=False)
        return self.value_set_client
    
    def get_medication_client(self) -> MedicationClient:
        if not self.medication_client:
            self.medication_client = MedicationClient(base_url=self.configuration.get_fonctions_allegees_url(), 
                                                      base_uri=self.configuration.get_fonctions_allegees_uri(), 
                                                      token_header=self.__build_headers(),
                                                      validate_certs=False)
        return self.medication_client
    
    def get_practitioner_client(self) -> PractitionerClient:
        if not self.practitioner_client:
            self.practitioner_client = PractitionerClient(base_url=self.configuration.get_fonctions_allegees_url(), 
                                                          base_uri=self.configuration.get_fonctions_allegees_uri(), 
                                                          token_header=self.__build_headers(),
                                                          validate_certs=False)
        return self.practitioner_client
    
    def get_location_client(self) -> LocationClient:
        if not self.location_client:
            self.location_client = LocationClient(base_url=self.configuration.get_fonctions_allegees_url(), 
                                                  base_uri=self.configuration.get_fonctions_allegees_uri(), 
                                                  token_header=self.__build_headers(),
                                                  validate_certs=False)
        return self.location_client

    def get_organization_client(self) -> OrganizationClient:
        if not self.organization_client:
            self.organization_client = OrganizationClient(base_url=self.configuration.get_fonctions_allegees_url(), 
                                                  base_uri=self.configuration.get_fonctions_allegees_uri(), 
                                                  token_header=self.__build_headers(),
                                                  validate_certs=False)
        return self.organization_client

    def get_condition_client(self) -> ConditionClient:
        if not self.condition_client:
            self.condition_client = ConditionClient(base_url=self.configuration.get_fonctions_allegees_url(), 
                                                    base_uri=self.configuration.get_fonctions_allegees_uri(), 
                                                    token_header=self.__build_headers(),
                                                    validate_certs=False)
        return self.condition_client

    def get_flag_client(self) -> FlagClient:
        if not self.flag_client:
            self.flag_client = FlagClient(base_url=self.configuration.get_fonctions_allegees_url(), 
                                                    base_uri=self.configuration.get_fonctions_allegees_uri(), 
                                                    token_header=self.__build_headers(),
                                                    validate_certs=False)
        return self.flag_client
     
    def get_validateur_usager(self) -> ValidateurUsager:
        if not self.validateur_usager:
            self.validateur_usager = ValidateurUsager(value_set_client=self.get_value_set_client())
        return self.validateur_usager
    
    def get_validateur_usager_pour_appariement(self) -> ValidateurUsagerPourAppariement:
        if not self.validateur_usager_pour_appariement:
            self.validateur_usager_pour_appariement = ValidateurUsagerPourAppariement()
        return self.validateur_usager_pour_appariement
    
    def get_validateur_acte_vaccinal(self) -> ValidateurActeVaccinal:
        if not self.validateur_acte_vaccinal:
            self.validateur_acte_vaccinal = ValidateurActeVaccinal(validateur_usager_pour_appariement=self.get_validateur_usager_pour_appariement(), 
                                                  value_set_client=self.get_value_set_client(),
                                                  medication_client=self.get_medication_client(),
                                                  practitioner_client=self.get_practitioner_client(),
                                                  location_client=self.get_location_client())
        return self.validateur_acte_vaccinal

    def get_convertisseur_usager(self) -> ConvertisseurUsager:
        if not self.convertisseur_usager:
            self.convertisseur_usager = ConvertisseurUsager()
        return self.convertisseur_usager
    
    def get_convertisseur_acte_vaccinal(self) -> ConvertisseurActeVaccinal:
        if not self.convertisseur_acte_vaccinal:
            self.convertisseur_acte_vaccinal = ConvertisseurActeVaccinal(convertisseur_usager=self.get_convertisseur_usager(), 
                                                                         patient_client=self.get_patient_client())
        return self.convertisseur_acte_vaccinal
    
    def get_chargeur_fichiers(self) -> ChargeurFichiers:
        if not self.chargeur_fichiers:
            self.chargeur_fichiers = ChargeurFichiers(self.configuration.get_files_path())
        return self.chargeur_fichiers
    
    def get_chargement_service(self) -> ChargementService:
        if not self.chargement_service:
            self.chargement_service = ChargementService(chargeur_fichiers=self.get_chargeur_fichiers(), 
                            validateur_usager=self.get_validateur_usager(), 
                            validateur_acte_vaccinal=self.get_validateur_acte_vaccinal(),
                            convertisseur_usager=self.get_convertisseur_usager(),
                            convertisseur_acte_vaccinal=self.get_convertisseur_acte_vaccinal(),
                            patient_client=self.get_patient_client(),
                            immunization_client=self.get_immunization_client())
        return self.chargement_service
            
    def __build_headers(self):
        return {"Authorization": self.configuration.get_authorization_header()}