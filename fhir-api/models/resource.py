import uuid
from flask import jsonify

from pymongo.errors import DuplicateKeyError

from errors.operation_outcome import OperationOutcome
from db import get_store


class Resource:
    resource = None

    def __init__(self, id=None, resource=None):
        """Initializes a Resource resource instance.
        The ID must be provided if the resource already exists.
        """
        if not resource and not id:
            raise OperationOutcome("An id or a resource must be provided")
        self.db = get_store()
        self.id = id or resource.get("id")
        self.resource = resource
        self.resource_type = type(self).__name__

    def json(self):
        """Returns the JSON serialization of the Resource resource"""
        if self.resource:
            return jsonify(self.resource)
        return jsonify({"id": self.id})

    def create(self):
        """Creates a Resource instance in fhirstore."""
        if not self.resource:
            raise OperationOutcome("Missing resource data to create a Resource")

        self.id = self.id or str(uuid.uuid4())

        try:
            self.resource = self.db.create(
                {**self.resource, "resourceType": self.resource_type, "id": self.id}
            )
        except DuplicateKeyError:
            raise OperationOutcome(f"Resource {self.id} already exists")

        return self

    def read(self):
        """Returns a Resource instance filled with the fhirstore data."""
        if not self.id:
            raise OperationOutcome("Resource ID is required")

        self.resource = self.db.read(self.resource_type, self.id)
        return self

    def update(self, resource):
        """Updates a Resource instance in fhirstore.
        If provided, resource.id must match self.id"""
        if not resource:
            raise OperationOutcome("Resource data is required to update a resource")
        if not self.id:
            raise OperationOutcome("Resource ID is required")
        if resource.get("id") and resource.get("id") != self.id:
            raise OperationOutcome("Resource id and update payload do not match")

        self.resource = self.db.update(self.resource_type, self.id, resource)
        return self

    def patch(self, patch):
        """Performs a patch operation on a Resource instance in fhirstore.
        If provided, patch.id must match self.id"""
        if not patch:
            raise OperationOutcome("Patch data is required to patch a resource")
        if not self.id:
            raise OperationOutcome("Resource ID is required to patch a resource")
        if patch.get("id") is not None and patch.get("id") != self.id:
            raise OperationOutcome("Resource id and patch payload do not match")

        self.resource = self.db.patch(self.resource_type, self.id, patch)
        return self

    def delete(self):
        if not self.id:
            raise OperationOutcome("Resource ID is required to delete it")

        self.resource = self.db.delete(self.resource_type, self.id)
        self.id = None
        return self

    def search(self, args):
        """Searchs a resource by calling fhirstore search function
        """
        results = self.db.comprehensive_search(self.resource_type, args)
        return results

    def history(self):
        pass
