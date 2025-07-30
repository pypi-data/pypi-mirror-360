import os
import json
from json.decoder import JSONDecodeError
from typing import List
import logging

log = logging.getLogger(__name__)

class ChargeurFichiers:

    def __init__(self, chemin: str = None) -> None:
        if chemin:
            self.chemin: str = chemin if chemin.endswith("/") or chemin.endswith("\\") else chemin + "/"
        else:
            self.chemin:str = None

    def obtenir_noms_fichiers(self) -> List[str]:
        fichiers: List[str] = []
        for f in os.listdir(self.chemin):
            if os.path.isfile(self.chemin + f if self.chemin else f) and f.endswith('.json'):
                fichiers.append(self.chemin + f if self.chemin else f)
        log.info("Les fichiers du répertoire {} ont été obtenus".format(self.chemin if self.chemin else "racine au traitement"))
        return sorted(fichiers)
    
    def obtenir_contenu_fichier_par_nom(self, fichier) -> List[str]:
        f = open(fichier, encoding='utf-8')
        objet = None
        try:
            objet = json.loads(f.read())
            log.info("Le fichier {} a été décodé avec succèes".format(fichier))
        except JSONDecodeError:
            log.error("Le fichier {} n'a pas pu être décodé en format json. Il est invalide".format(fichier))
        f.close()
        return objet