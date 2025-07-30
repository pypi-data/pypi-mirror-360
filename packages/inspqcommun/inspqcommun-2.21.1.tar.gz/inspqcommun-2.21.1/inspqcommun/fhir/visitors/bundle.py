from fhirclient.models.bundle import Bundle, BundleEntry
from inspqcommun.fhir.visitors.base import BaseVisitor

class BundleVisitor(BaseVisitor):

    def __init__(self, fhir_resource=None):
        self.entries = []
        self.setFhirResource(fhir_resource if fhir_resource else Bundle())

    def getFhirResource(self) -> Bundle:
        return super().getFhirResource()

    def add_entry(self, resource, response=None):
        entry = BundleEntry()
        entry.resource = resource
        if response:
            entry.response = response

        if not self.getFhirResource().entry:
            self.getFhirResource().entry = []
        self.getFhirResource().entry.append(entry)

    def count_entries(self, recurse=False, resource_type=None):
        return len(self.get_entries(recurse=recurse, resource_type=resource_type))

    def get_entries(self, recurse=False, resource_type=None):
        entries = []
        if self.getFhirResource().entry is None:
            return []
        if recurse:
            for entry in self.getFhirResource().entry:
                if resource_type is None or entry.resource.resource_name == resource_type:
                    entries.append(entry.resource)
                if type(entry.resource) is Bundle:
                    bundle_fhir = BundleVisitor(fhir_resource=entry.resource)
                    sub_entries = bundle_fhir.get_entries(recurse=recurse, resource_type=resource_type)
                    for e in sub_entries:
                        entries.append(e)
            return entries
        else:
            return self.getFhirResource().entry
        