import uuid
from typing import Dict, Union

from fhir.resources import FHIRAbstractModel
from fhir.resources.bundle import Bundle
from fhir.resources.operationoutcome import OperationOutcome
from flask import jsonify

import fhirstore
from fhir_api.db import get_store
from fhir_api.errors import BadRequest


class BaseResource:
    resource: Union[None, FHIRAbstractModel] = None

    def __init__(self, id=None, resource: Union[None, Dict, FHIRAbstractModel] = None):
        """Initializes a Resource resource instance.
        The ID must be provided if the resource already exists.
        """
        if not resource and not id:
            raise BadRequest("An id or a resource must be provided")

        self.db = get_store()
        self.resource_type = type(self).__name__

        if resource:
            self.resource = self.db.normalize_resource(resource)
            self.id = self.resource.id
        else:
            self.id = id

    def json(self) -> str:
        """Returns the JSON serialization of the Resource resource"""
        if self.resource:
            return jsonify(self.resource.dict())
        return jsonify({"id": self.id})

    def create(self) -> Union[FHIRAbstractModel, OperationOutcome]:
        """Creates a Resource instance in fhirstore."""
        if not self.resource:
            raise BadRequest("Missing resource data to create a resource")

        # generate a uuid for the resource if it doesn't have one already
        self.id = self.id or str(uuid.uuid4())
        if not self.resource.id:
            self.resource.id = self.id

        res = self.db.create(self.resource)
        if not isinstance(res, OperationOutcome):
            self.resource = res
        return res

    def read(self) -> Union[FHIRAbstractModel, OperationOutcome]:
        """Returns a Resource instance filled with the fhirstore data."""
        if not self.id:
            raise BadRequest("Resource ID is required")

        res = self.db.read(self.resource_type, self.id)
        if not isinstance(res, OperationOutcome):
            self.resource = res
        return res

    def update(self, resource) -> Union[FHIRAbstractModel, OperationOutcome]:
        """Updates a Resource instance in fhirstore.
        If provided, resource.id must match self.id"""
        if not resource:
            raise BadRequest("Resource data is required to update a resource")
        if not self.id:
            raise BadRequest("Resource ID is required")
        if resource.get("id") and resource.get("id") != self.id:
            raise BadRequest("Resource id and update payload do not match")

        res = self.db.update(self.id, resource)
        if not isinstance(res, OperationOutcome):
            self.resource = res
        return res

    def patch(self, patch) -> Union[FHIRAbstractModel, OperationOutcome]:
        """Performs a patch operation on a Resource instance in fhirstore.
        If provided, patch.id must match self.id"""
        if not patch:
            raise BadRequest("Patch data is required to patch a resource")
        if not self.id:
            raise BadRequest("Resource ID is required to patch a resource")
        if patch.get("id") is not None and patch.get("id") != self.id:
            raise BadRequest("Resource id and patch payload do not match")

        res = self.db.patch(self.resource_type, self.id, patch)
        if not isinstance(res, OperationOutcome):
            self.resource = res
        return res

    def delete(self) -> OperationOutcome:
        if not self.id:
            raise BadRequest("Resource ID is required to delete it")

        try:
            # res is always a OperationOutcome resource, return it as is.
            res = self.db.delete(self.resource_type, self.id)
        except fhirstore.BadRequestError as e:
            raise BadRequest(str(e))

        self.resource = None
        self.id = None
        return res

    def search(self, query_string=None, params=None) -> Union[Bundle, OperationOutcome]:
        """Searchs a resource by calling fhirstore search function"""
        return self.db.search(self.resource_type, query_string=query_string, params=params)

    def history(self):
        pass
