from datetime import date
from typing import List
from inspqcommun.fa.ressources.ressource import Ressource
from inspqcommun.fa.ressources.usager import Usager   
from inspqcommun.fa.ressources.vaccinateur import Vaccinateur
from inspqcommun.fa.ressources.lieu_vaccination import LieuVaccination 

class ActeVaccinal(Ressource):

    def __init__(self, **kwargs) -> None:
        self.usager : Usager = self._get_value_from_kwargs("usager", Usager, **kwargs)
        self.nomCommercial : str = self._get_value_from_kwargs("nomCommercial", **kwargs)
        self.agent : str = self._get_value_from_kwargs("agent", **kwargs)
        self.lot : ActeVaccinal.Lot = self._get_value_from_kwargs("lot", ActeVaccinal.Lot, **kwargs)
        self.dateAdministration : date = self._get_value_from_kwargs("dateAdministration", defaultValue=date.today(), **kwargs)
        self.quantiteAdministree : ActeVaccinal.QuantiteAdministree = self._get_value_from_kwargs("quantiteAdministree", ActeVaccinal.QuantiteAdministree, **kwargs)
        self.voieAdministration : str = self._get_value_from_kwargs("voieAdministration", **kwargs)
        self.siteAdministration : str = self._get_value_from_kwargs("siteAdministration", **kwargs)
        self.raisonAdministration : str = self._get_value_from_kwargs("raisonAdministration", **kwargs)
        self.vaccinateur : Vaccinateur = self._get_value_from_kwargs("vaccinateur", Vaccinateur, **kwargs)
        self.lieuVaccination : LieuVaccination = self._get_value_from_kwargs("lieuVaccination", LieuVaccination, **kwargs)
        self.commentaires : List[ActeVaccinal.Commentaire] = self._get_list_of_values_from_kwargs("commentaires", ActeVaccinal.Commentaire, **kwargs)
        
        super().__init__("ActeVaccinal")            

    class QuantiteAdministree(Ressource):

        def __init__(self, **kwargs) -> None:
            self.quantite : float = self._get_value_from_kwargs("quantite", **kwargs)
            self.unite : str = self._get_value_from_kwargs("unite", **kwargs)
    
    class Commentaire(Ressource):

        def __init__(self, **kwargs) -> None:
            self.auteur : str = self._get_value_from_kwargs("auteur", **kwargs) 
            self.date : date = self._get_value_from_kwargs("date", **kwargs)
            self.texte : str = self._get_value_from_kwargs("texte", **kwargs)
    
    class Lot(Ressource):

        def __init__(self, **kwargs) -> None:
            self.id : int = self._get_value_from_kwargs("id", **kwargs)
            self.numero : str = self._get_value_from_kwargs("numero", **kwargs)