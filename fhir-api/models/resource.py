from flask import jsonify

from db import get_db_connection


class Resource:
    resource = None

    def __init__(self, id=None, resource=None):
        """Initializes a Resource resource instance.
        The ID must be provided if the resource already exists.
        """
        if not resource and not id:
            raise Exception('An id or a resource must be provided')
        self.db = get_db_connection()
        self.id = id
        self.resource = resource
        self.resource_type = type(self).__name__

    def json(self):
        """Returns the JSON serialization of the Resource resource"""
        if self.resource:
            return jsonify(self.resource)
        return jsonify({'id': self.id})

    def create(self):
        """Creates a Resource instance in fhirbase."""
        if not self.resource:
            raise Exception('Missing resource data to create a Resource')
        if self.id:
            raise Exception('Cannot create a resource with an ID')

        if self.resource.get('id'):
            del resource['id']
        self.resource = self.db.create({
            'resourceType': self.resource_type,
            **self.resource
        })
        self.id = self.resource['id']
        return self

    def read(self):
        """Returns a Resource instance filled with the fhirbase data."""
        if not self.id:
            raise Exception('Resource ID is required')

        self.resource = self.db.read({
            'resourceType': self.resource_type,
            'id': self.id
        })
        return self

    def update(self, resource):
        """Updates a Resource instance in fhirbase.
        If provided, resource.id must match self.id"""
        if not resource:
            raise Exception('Resource data is required to update a resource')
        if not self.id:
            if resource.get('id'):
                del resource['id']
            self.resource = self.db.create({
                'resourceType': self.resource_type,
                **resource
            })
            self.id = self.resource['id']
        else:
            if self.read().resource is None:
                raise Exception(f'Resource {self.id} does not exist')
            self.resource = self.db.update({
                'id': self.id,
                'resourceType': self.resource_type,
                **resource
            })
        return self

    def patch(self, patch):
        """Performs a patch operation on a Resource instance in fhirbase."""
        if not patch:
            raise Exception('Patch data is required to patch a resource')
        if not self.id:
            raise Exception('Resource ID is required to patch a resource')

        self.read()
        self.resource = self.db.update({
            'resourceType': self.resource_type,
            **self.resource,
            **patch
        })
        return self

    def delete(self):
        if not self.id:
            raise Exception('Resource ID is required to delete it')

        self.resource = self.db.delete({
            'resourceType': self.resource_type,
            'id': self.id
        })
        self.id = None
        return self

    def history(self):
        pass
