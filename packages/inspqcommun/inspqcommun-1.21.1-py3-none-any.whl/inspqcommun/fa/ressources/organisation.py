from inspqcommun.fa.ressources.ressource import Ressource

class Organisation(Ressource):

    def __init__(self, **kwargs) -> None:
        super().__init__("Organisation")
        self.id : int = self._get_value_from_kwargs("id", **kwargs)
        self.nom : str = self._get_value_from_kwargs("nom", **kwargs)