from fhirclient.models.extension import Extension
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.coding import Coding
from datetime import datetime

class BaseVisitor():
    DEFAULT_CODING_SYSTEM = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary'
    DEFAULT_CODING_VERSION = "1.0.0"

    __fhir_resource = None
    def __eq__(self, value: object) -> bool:
        return self.getFhirResource().as_json() == value.getFhirResource().as_json()
    
    def __contains__(self, value: object) -> bool:
        return self._is_struct_included(
            value.getFhirResource().as_json(),
            self.getFhirResource().as_json())
    
    def merge(self, value: object) -> None:
        if self.__fhir_resource is None:
            self.__fhir_resource = value.getFhirResource()
        else:
            self_json = self.getFhirResource().as_json()
            value_json = value.getFhirResource().as_json()
            self_json.update(value_json)
            new_fhir_resource = type(self.__fhir_resource)(jsondict=self_json)
            self.setFhirResource(new_fhir_resource)
            
    def getFhirResource(self):
        return self.__fhir_resource
    
    def setFhirResource(self, fhir_resource):
        self.__fhir_resource = fhir_resource

    def str_date_to_fhir_date(self, str_date):
        fhir_date  = FHIRDate()
        fhir_date.date = datetime.strptime(str_date, '%Y-%m-%d').date()
        return fhir_date

    def fhir_date_to_str_date(self, fhir_date):
        str_date = None
        if fhir_date is not None and fhir_date.date is not None:
            str_date = fhir_date.isostring
        return str_date

    def add_or_update_extension_to_extensions(self, extension, extensions):
        if extensions is None:
            extensions = [extension]
        else:
            ext_found = False
            for ext in extensions:
                if type(ext) is Extension:
                    if ext.url == extension.url:
                        extensions.remove(ext)
                        extensions.append(extension)
                        ext_found = True
                        break
                elif type(ext) is list:
                    for sub_ext in ext:
                        ext = self.add_or_update_extension_to_extensions(extension=sub_ext, extensions=ext)
            if not ext_found:
                extensions.append(extension)
        return extensions
    
    def _to_codeable_concept(self, code: str, display:str=None, coding_system: str=DEFAULT_CODING_SYSTEM, coding_version: str=DEFAULT_CODING_VERSION) -> CodeableConcept:
        codeableConcept = CodeableConcept()
        coding = Coding()
        coding.code = code
        if display:
            coding.display = display
        coding.system = coding_system
        coding.version = coding_version
        codeableConcept.coding = [coding]
        return codeableConcept
    
    def _get_coding_par_system(self, codeableConcept: CodeableConcept, coding_system:str=DEFAULT_CODING_SYSTEM, coding_version:str=DEFAULT_CODING_VERSION) -> Coding:
        coding: Coding
        coding_without_system = None
        for coding in codeableConcept.coding:
            if coding.system == coding_system and coding.version == coding_version:
                return coding
            elif coding.system is None:
                coding_without_system = coding 
        return coding_without_system
    
    def _creer_extension(self, url: str, **kwargs) -> Extension:
        extension = Extension()
        extension.url = url
        if "valueString" in kwargs:
            extension.valueString = kwargs["valueString"]
        elif "valueDate" in kwargs:
            extension.valueDate = kwargs["valueDate"]
        elif "valueCodeableConcept" in kwargs:
            extension.valueCodeableConcept = kwargs["valueCodeableConcept"]
        elif "valueInteger" in kwargs:
            extension.valueInteger = kwargs["valueInteger"]
        return extension
    
    def _is_struct_included(self, struct1, struct2, exclude=None):
        """
        This function compare if the first parameter structure is included in the second.
        The function use every elements of struct1 and validates they are present in the struct2 structure.
        The two structure does not need to be equals for that function to return true.
        Each elements are compared recursively.
        :param struct1:
            type:
                dict for the initial call, can be dict, list, bool, int or str for recursive calls
            description:
                reference structure
        :param struct2:
            type:
                dict for the initial call, can be dict, list, bool, int or str for recursive calls
            description:
                structure to compare with first parameter.
        :param exclude:
            type:
                list
            description:
                Key to exclude from the comparison.
            default: None
        :return:
            type:
                bool
            description:
                Return True if all element of dict 1 are present in dict 2, return false otherwise.
        """
        if isinstance(struct1, list) and isinstance(struct2, list):
            if not struct1 and not struct2:
                return True
            for item1 in (struct1):
                if isinstance(item1, (list, dict)):
                    for item2 in (struct2):
                        if self._is_struct_included(item1, item2, exclude):
                            break
                    else:
                        return False
                else:
                    if item1 not in struct2:
                        return False
            return True
        elif isinstance(struct1, dict) and isinstance(struct2, dict):
            if not struct1 and not struct2:
                return True
            try:
                for key in struct1:
                    if not (exclude and key in exclude):
                        if not self._is_struct_included(struct1[key], struct2[key], exclude):
                            return False
            except KeyError:
                return False
            return True
        elif type(struct1) is str and type(struct2) is str:
            return struct1 in struct2
        else:
            return struct1 == struct2
