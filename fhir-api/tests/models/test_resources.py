from unittest.mock import patch

import pytest
from fhir.resources.patient import Patient

from fhir_api.errors import BadRequest
from fhir_api.models.base import BaseResource


@patch("fhir_api.models.base.get_store", autospec=True)
class TestResource:
    def test_init_with_id_no_resource(self, mock_get_store):
        """Gets the DB connection and initializes id and resource_type"""
        resource_id = "id"
        r = BaseResource(id=resource_id)
        assert mock_get_store.call_count == 1
        assert r.db == mock_get_store.return_value

        assert r.id == "id"
        assert r.resource is None
        assert r.resource_type == "BaseResource"

    def test_init_with_resource(self, mock_get_store):
        """Initializes resource and resource_type"""
        resource_data = {"gender": "female"}
        mock_get_store.return_value.normalize_resource.return_value = Patient(**resource_data)

        r = BaseResource(resource=resource_data)
        assert mock_get_store.call_count == 1
        assert r.db == mock_get_store.return_value

        assert r.id is None
        assert r.resource == Patient(**resource_data)
        assert r.resource_type == "BaseResource"

    def test_init_without_id_nor_resource(self, mock_get_store):
        """Raises an error if no id nor resource are provided"""
        with pytest.raises(
            BadRequest,
            match="An id or a resource must be provided",
        ):
            BaseResource()
        assert mock_get_store.call_count == 0

    @patch("uuid.uuid4", return_value="uuid")
    def test_create(self, mock_uuid, mock_get_store):
        """Test create method.

        Calls the create method of the fhirstore client
        and registers the ID
        """
        resource = Patient(gender="male")
        mock_get_store.return_value.normalize_resource.return_value = resource

        mock_get_store.return_value.create.return_value = resource
        mock_get_store.return_value.read.return_value = None
        r = BaseResource(resource=resource)

        r.create()
        mock_get_store.return_value.create.assert_called_once_with(resource)
        assert r.id == "uuid"
        assert r.resource == resource

    def test_create_missing_resource(self, mock_get_store):
        """Raises an error when the resource data was not provided at init"""
        r = BaseResource(id="id")
        with pytest.raises(BadRequest, match="Missing resource data to create a resource"):
            r.create()
        assert mock_get_store.return_value.create.call_count == 0

    def test_create_extra_id(self, mock_get_store):
        """Accepts the resource data when an id was provided"""
        resource = Patient(id="test")
        mock_get_store.return_value.normalize_resource.return_value = resource
        mock_get_store.return_value.create.return_value = resource
        mock_get_store.return_value.read.return_value = None

        r = BaseResource(resource=resource)

        r.create()
        assert r.id == "test"
        assert r.resource == resource

    def test_read(self, mock_get_store):
        """Test read method.

        Calls the read method of the fhirstore client
        and registers the resource.
        """
        resource = Patient(id="test")
        mock_get_store.return_value.normalize_resource.return_value = resource
        mock_get_store.return_value.read.return_value = resource

        r = BaseResource(id="test")

        r.read()
        mock_get_store.return_value.read.assert_called_once_with("BaseResource", "test")
        assert r.resource == resource

    def test_read_missing_id(self, mock_get_store):
        """Raises an error when the id was not provided at init"""
        resource = Patient()
        mock_get_store.return_value.normalize_resource.return_value = resource
        r = BaseResource(resource=resource)

        with pytest.raises(BadRequest, match="Resource ID is required"):
            r.read()
        assert mock_get_store.return_value.read.call_count == 0

    def test_update_without_id(self, mock_get_store):
        """Test update without id.

        Calls the update method of the fhirstore client
        and creates the resource.
        """
        resource = Patient(id="test")
        mock_get_store.return_value.normalize_resource.return_value = resource
        mock_get_store.return_value.update.return_value = Patient(id="test", gender="other")

        update_data = {"gender": "other"}
        r = BaseResource(resource=resource)
        r.update(update_data)

        mock_get_store.return_value.update.assert_called_once_with("test", update_data)
        assert r.resource == Patient(id="test", gender="other")

    def test_update_with_id(self, mock_get_store):
        """Test update with id.

        Calls the update method of the fhirstore client
        and registers the resource
        """
        resource = Patient(id="test")
        mock_get_store.return_value.normalize_resource.return_value = resource
        mock_get_store.return_value.update.return_value = Patient(id="test", gender="other")

        update_data = {"gender": "other"}
        r = BaseResource(id="test", resource=resource)
        r.update(update_data)

        mock_get_store.return_value.update.assert_called_once_with("test", update_data)
        assert r.resource == Patient(id="test", gender="other")

    def test_update_id_dont_match(self, mock_get_store):
        """Raises an error when the resource was not provided"""
        r = BaseResource(id="1")

        with pytest.raises(
            BadRequest,
            match="Resource id and update payload do not match",
        ):
            r = r.update({"id": "2"})
        assert mock_get_store.return_value.update.call_count == 0

    def test_update_missing_resource(self, mock_get_store):
        """Raises an error when the resource was not provided"""
        r = BaseResource(id="1")

        with pytest.raises(
            BadRequest,
            match="Resource data is required to update a resource",
        ):
            r = r.update(None)
        assert mock_get_store.return_value.update.call_count == 0

    def test_patch(self, mock_get_store):
        """Applies a patch on the resource by reading and then updating it"""
        resource = Patient(id="test")
        mock_get_store.return_value.normalize_resource.return_value = resource
        mock_get_store.return_value.patch.return_value = Patient(id="test", gender="other")

        patch_data = {"gender": "other"}
        r = BaseResource(id="test", resource=resource)
        r.patch(patch_data)

        mock_get_store.return_value.patch.assert_called_once_with(
            "BaseResource", "test", patch_data
        )
        assert r.resource == Patient(id="test", gender="other")

    def test_patch_missing_data(self, mock_get_store):
        """Raises an error when the patch data is not provided"""
        resource = Patient(id="test")
        mock_get_store.return_value.normalize_resource.return_value = resource
        r = BaseResource(id="test")

        with pytest.raises(
            BadRequest,
            match="Patch data is required to patch a resource",
        ):
            r.patch(None)
        assert mock_get_store.return_value.patch.call_count == 0

    def test_patch_missing_id(self, mock_get_store):
        """Raises an error when the resource id was not provided at init"""
        resource = Patient(gender="test")
        mock_get_store.return_value.normalize_resource.return_value = resource
        r = BaseResource(resource=resource)

        with pytest.raises(
            BadRequest,
            match="Resource ID is required to patch a resource",
        ):
            r.patch({"some": "patch"})
        assert mock_get_store.return_value.patch.call_count == 0

    def test_delete(self, mock_get_store):
        """Calls the delete method of the fhirstore client"""
        resource = Patient(id="test")
        mock_get_store.return_value.normalize_resource.return_value = resource
        r = BaseResource(resource=resource)

        r.delete()

        mock_get_store.return_value.delete.assert_called_once_with("BaseResource", "test")
        assert r.resource is None
        assert r.id is None

    def test_delete_missing_id(self, mock_get_store):
        """Raises an error when the patch data is not provided"""
        resource = Patient()
        mock_get_store.return_value.normalize_resource.return_value = resource
        r = BaseResource(resource=resource)

        with pytest.raises(
            BadRequest,
            match="Resource ID is required to delete it",
        ):
            r = r.delete()
        assert mock_get_store.return_value.update.call_count == 0

    @patch("fhir_api.models.base.jsonify")
    def test_json_with_resource(self, mock_jsonify, mock_get_store):
        resource = Patient(id="test")
        mock_get_store.return_value.normalize_resource.return_value = resource
        r = BaseResource(resource=resource)

        r.json()
        mock_jsonify.assert_called_once_with(resource.dict())

    @patch("fhir_api.models.base.jsonify")
    def test_json_with_id(self, mock_jsonify, mock_get_store):
        r = BaseResource(id="test")

        r.json()
        mock_jsonify.assert_called_once_with({"id": "test"})
