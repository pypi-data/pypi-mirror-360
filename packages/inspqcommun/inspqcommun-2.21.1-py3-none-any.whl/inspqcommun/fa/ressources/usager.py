from inspqcommun.fa.ressources.ressource import Ressource
from datetime import date
from typing import List

class Usager(Ressource):
    
    def __init__(self, **kwargs) -> None:
        self.identifiants : List[Usager.Identifiant] = self._get_list_of_values_from_kwargs("identifiants", Usager.Identifiant, **kwargs)
        self.prenom : str =  self._get_value_from_kwargs("prenom", defaultValue='', **kwargs)
        self.nom : str = self._get_value_from_kwargs("nom", defaultValue='', **kwargs)
        self.dateNaissance : date = self._get_value_from_kwargs("dateNaissance", **kwargs)
        self.sexe : str = self._get_value_from_kwargs("sexe", defaultValue='', **kwargs)
        self.adresse : Usager.Adresse = self._get_value_from_kwargs("adresse", Usager.Adresse, **kwargs)
        self.telephone : Usager.Telephone = self._get_value_from_kwargs("telephone", Usager.Telephone, **kwargs)
        self.contacts : List[Usager.Contact] = self._get_list_of_values_from_kwargs("contacts", Usager.Contact, **kwargs)
        
        super().__init__("Usager")            

    class Identifiant(Ressource):
        
        def __init__(self, **kwargs) -> None:
            self.type : str = self._get_value_from_kwargs("type", **kwargs)
            self.valeur : str = self._get_value_from_kwargs("valeur", **kwargs)
    
    class Adresse(Ressource):

        def __init__(self, **kwargs) -> None:
            self.adresse : str = self._get_value_from_kwargs("adresse", **kwargs)
            self.ville : str = self._get_value_from_kwargs("ville", **kwargs)
            self.province : str  = self._get_value_from_kwargs("province", **kwargs)
            self.pays : str = self._get_value_from_kwargs("pays", **kwargs)
            self.codePostal : str = self._get_value_from_kwargs("codePostal", **kwargs)
        
        def get_province_code(self) -> str:
            if self.province:
                if self.province.lower() == 'ontario':
                    return 'ON'
            return 'QC'

    class Contact(Ressource):

        def __init__(self, **kwargs) -> None:
            self.type : str = self._get_value_from_kwargs("type", **kwargs)
            self.prenom : str = self._get_value_from_kwargs("prenom", **kwargs)
            self.nom : str = self._get_value_from_kwargs("nom", **kwargs)

    class Telephone(Ressource):

        def __init__(self, **kwargs) -> None:
            self.numero : str = self._get_value_from_kwargs("numero", **kwargs)
            self.extension : str = self._get_value_from_kwargs("extension", **kwargs)