import json

class Ressource:
    
    ressource: str

    def __init__(self, ressource: str) -> None:
        self.ressource = ressource

    def as_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else str(o), sort_keys=True, indent=4)

    def _get_value_from_kwargs(self, key: str, clazz=None, defaultValue=None, **kwargs):
        if clazz:
            return clazz(**kwargs[key]) if kwargs and key in kwargs and kwargs[key] else defaultValue
        else:
            return kwargs[key] if kwargs and key in kwargs and kwargs[key] else defaultValue
    
    def _get_list_of_values_from_kwargs(self, key: str, clazz=None, defaultValue=None, **kwargs):
        if kwargs and key in kwargs and kwargs[key]:
            if clazz:
                return [ clazz(**valeur) for valeur in kwargs[key] ]
            else:
                return [ valeur for valeur in kwargs[key] ]
        else:
            return defaultValue if defaultValue else []