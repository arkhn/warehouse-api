import pytest
from unittest.mock import patch

from models.resource import Resource
from errors.operation_outcome import OperationOutcome


@patch("models.resource.get_store", autospec=True)
class TestResource:
    def test_init_with_id_no_resource(self, mock_get_store):
        """Gets the DB connection and initializes id and resource_type"""
        resource_id = "id"
        r = Resource(id=resource_id)
        assert mock_get_store.call_count == 1
        assert r.db == mock_get_store.return_value

        assert r.id == "id"
        assert r.resource is None
        assert r.resource_type == "Resource"

    def test_init_with_resource(self, mock_get_store):
        """Initializes resource and resource_type"""
        resource_data = {"my": "resource"}
        r = Resource(resource=resource_data)
        assert mock_get_store.call_count == 1
        assert r.db == mock_get_store.return_value

        assert r.id is None
        assert r.resource == resource_data
        assert r.resource_type == "Resource"

    def test_init_without_id_nor_resource(self, mock_get_store):
        """Raises an error if no id nor resource are provided"""
        with pytest.raises(
            OperationOutcome,
            match="An id or a resource must \
be provided",
        ):
            Resource()
        assert mock_get_store.call_count == 0

    @patch("uuid.uuid4", return_value="uuid")
    def test_create(self, mock_uuid, mock_get_store):
        """Calls the create method of the fhirstore client and registers the ID
        """
        resource_data = {"my": "resource"}
        create_ret_data = {**resource_data, "_id": "0541"}
        mock_get_store.return_value.create.return_value = create_ret_data
        mock_get_store.return_value.read.return_value = None
        r = Resource(resource=resource_data)

        r = r.create()
        mock_get_store.return_value.create.assert_called_once_with(
            {"resourceType": "Resource", "id": "uuid", **resource_data}
        )
        assert r.id == "uuid"
        assert r.resource == create_ret_data

    def test_create_missing_resource(self, mock_get_store):
        """Raises an error when the resource data was not provided at init"""
        r = Resource(id="id")
        with pytest.raises(OperationOutcome, match="Missing resource data to create a Resource"):
            r = r.create()
        assert mock_get_store.return_value.create.call_count == 0

    def test_create_extra_id(self, mock_get_store):
        """Accepts the resource data when an id was provided"""
        resource_data = {"my": "resource", "id": "test"}
        create_ret_data = {**resource_data, "_id": "0541"}
        mock_get_store.return_value.create.return_value = create_ret_data
        mock_get_store.return_value.read.return_value = None
        r = Resource(resource=resource_data)

        r = r.create()
        assert r.id == "test"
        assert r.resource == create_ret_data

    def test_read(self, mock_get_store):
        """Calls the read method of the fhirstore client and registers the resource
        """
        test_id = {"id": "id"}
        read_ret_data = {"my": "resource", **test_id}
        mock_get_store.return_value.read.return_value = read_ret_data
        r = Resource(id=test_id["id"])

        r = r.read()
        mock_get_store.return_value.read.assert_called_once_with("Resource", test_id["id"])
        assert r.resource == read_ret_data

    def test_read_missing_id(self, mock_get_store):
        """Raises an error when the id was not provided at init"""
        r = Resource(resource={"some": "data"})

        with pytest.raises(OperationOutcome, match="Resource ID is required"):
            r = r.read()
        assert mock_get_store.return_value.read.call_count == 0

    def test_update_without_id(self, mock_get_store):
        """Calls the update method of the fhirstore client and creates the resource
        """
        test_id = {"id": "id"}
        resource_data = {"my": "resource", **test_id}
        update_data = {"test": "two"}
        r = Resource(resource=resource_data)

        r = r.update(update_data)
        mock_get_store.return_value.update.assert_called_once_with(
            "Resource", test_id["id"], update_data
        )
        assert r.id == test_id["id"]

    def test_update_with_id(self, mock_get_store):
        """Calls the update method of the fhirstore client and registers the resource
        """
        test_id = {"id": "id"}
        resource_data = {"my": "resource"}
        update_data = {"test": "two"}
        r = Resource(id=test_id["id"], resource=resource_data)

        r = r.update(update_data)
        mock_get_store.return_value.update.assert_called_once_with(
            "Resource", test_id["id"], update_data
        )
        assert r.id == test_id["id"]

    def test_update_id_dont_match(self, mock_get_store):
        """Raises an error when the resource was not provided"""
        r = Resource(id="1")

        with pytest.raises(
            OperationOutcome,
            match="Resource id and update \
payload do not match",
        ):
            r = r.update({"id": "2"})
        assert mock_get_store.return_value.update.call_count == 0

    def test_update_missing_resource(self, mock_get_store):
        """Raises an error when the resource was not provided"""
        r = Resource(id="1")

        with pytest.raises(
            OperationOutcome,
            match="Resource data is required to \
update a resource",
        ):
            r = r.update(None)
        assert mock_get_store.return_value.update.call_count == 0

    def test_patch(self, mock_get_store):
        """Applies a patch on the resource by reading and then updating it
        """
        test_id = {"id": "id"}
        patch_data = {"test": "two"}
        r = Resource(id=test_id["id"])

        r = r.patch(patch_data)
        mock_get_store.return_value.patch.assert_called_once_with(
            "Resource", test_id["id"], patch_data
        )
        assert r.id == test_id["id"]

    def test_patch_missing_data(self, mock_get_store):
        """Raises an error when the patch data is not provided
        """
        test_id = {"id": "id"}
        r = Resource(id=test_id["id"])

        with pytest.raises(
            OperationOutcome,
            match="Patch data is required to \
patch a resource",
        ):
            r = r.patch(None)
        assert mock_get_store.return_value.update.call_count == 0

    def test_patch_missing_id(self, mock_get_store):
        """Raises an error when the resource id was not provided at init"""
        r = Resource(resource={"some": "data"})

        with pytest.raises(
            OperationOutcome,
            match="Resource ID is required to \
patch a resource",
        ):
            r = r.patch({"some": "patch"})
        assert mock_get_store.return_value.update.call_count == 0

    def test_delete(self, mock_get_store):
        """Calls the delete method of the fhirstore client
        """
        test_id = {"id": "id"}
        mock_get_store.return_value.delete.return_value = None
        r = Resource(id=test_id["id"])

        r = r.delete()
        mock_get_store.return_value.delete.assert_called_once_with("Resource", test_id["id"])
        assert r.resource is None
        assert r.id is None

    def test_delete_missing_id(self, mock_get_store):
        """Raises an error when the patch data is not provided
        """
        r = Resource(resource={"some": "data"})

        with pytest.raises(
            OperationOutcome,
            match="Resource ID is required to delete \
it",
        ):
            r = r.delete()
        assert mock_get_store.return_value.update.call_count == 0

    @patch("models.resource.jsonify")
    def test_json_with_resource(self, mock_jsonify, mock_get_store):
        resource_data = {"data": "test"}
        r = Resource(resource=resource_data)
        r.json()
        mock_jsonify.assert_called_once_with(resource_data)

    @patch("models.resource.jsonify")
    def test_json_with_id(self, mock_jsonify, mock_get_store):
        r = Resource(id="test")
        r.json()
        mock_jsonify.assert_called_once_with({"id": "test"})
