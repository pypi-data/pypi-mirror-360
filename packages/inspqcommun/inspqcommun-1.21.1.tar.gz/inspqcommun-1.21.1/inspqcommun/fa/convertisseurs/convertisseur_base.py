from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.coding import Coding

class ConvertisseurBase:
    
    def _convertirEnCodeableConcept(self, code: str) -> CodeableConcept:
        codeableConcept = CodeableConcept()
        coding = Coding()
        coding.code = code
        coding.system = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary'
        coding.version = '1.0.0'
        codeableConcept.coding = [ coding ]
        return codeableConcept