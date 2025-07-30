from inspqcommun.fa.ressources.ressource import Ressource

class Vaccinateur(Ressource):

    def __init__(self, **kwargs) -> None:
        super().__init__("Vaccinateur")
        self.id : int = self._get_value_from_kwargs("id", **kwargs)
        self.prenom : str = self._get_value_from_kwargs("prenom", **kwargs)
        self.nom : str = self._get_value_from_kwargs("nom", **kwargs)
        self.profession : str = self._get_value_from_kwargs("profession", **kwargs)
        self.numeroPermis : str = self._get_value_from_kwargs("numeroPermis", **kwargs)