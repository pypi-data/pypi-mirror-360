from inspqcommun.fa.ressources.ressource import Ressource
from inspqcommun.fa.ressources.organisation import Organisation

class LieuVaccination(Ressource):

    def __init__(self, **kwargs) -> None:
        super().__init__("LieuVaccination")
        self.id : int = self._get_value_from_kwargs("id", **kwargs)
        self.nom : str = self._get_value_from_kwargs("nom", **kwargs)
        self.organisationParente : Organisation = self._get_value_from_kwargs("organisationParente", Organisation, **kwargs)