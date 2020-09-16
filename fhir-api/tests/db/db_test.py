from unittest import TestCase
from unittest.mock import patch

from db import DB_NAME, get_db_connection, get_es_connection, get_store, reset_db_connection


@patch("fhirstore.FHIRStore")
@patch("pymongo.MongoClient")
@patch("elasticsearch.Elasticsearch")
class TestDB(TestCase):
    def tearDown(self):
        reset_db_connection()

    def test_get_db_connection_once(self, mock_es_client, mock_mongo_client, mock_fhirstore):
        """Initializes a pymongo.MongoClient."""
        assert mock_mongo_client.call_count == 0

        client = get_db_connection()
        assert mock_mongo_client.call_count == 1
        assert client == mock_mongo_client.return_value

    def test_get_db_connection_twice(self, mock_es_client, mock_mongo_client, mock_fhirstore):
        """Calling get_db_connection twice returns the same connection."""
        assert mock_mongo_client.call_count == 0

        client = get_db_connection()
        assert mock_mongo_client.call_count == 1
        assert client == mock_mongo_client.return_value

        client = get_db_connection()
        assert mock_mongo_client.call_count == 1
        assert client == mock_mongo_client.return_value

    def test_get_es_connection_once(self, mock_es_client, mock_mongo_client, mock_fhirstore):
        """Initializes a elasticSearch.Elasticsearch"""
        assert mock_es_client.call_count == 0

        client_es = get_es_connection()
        assert mock_es_client.call_count == 1
        assert client_es == mock_es_client.return_value

    def test_get_es_connection_twice(self, mock_es_client, mock_mongo_client, mock_fhirstore):
        """Calling get_es_connection twice returns the same connection."""
        assert mock_es_client.call_count == 0

        client_es = get_es_connection()
        assert mock_es_client.call_count == 1
        assert client_es == mock_es_client.return_value

        client_es = get_es_connection()
        assert mock_es_client.call_count == 1
        assert client_es == mock_es_client.return_value

    def test_get_store_once(self, mock_es_client, mock_mongo_client, mock_fhirstore):
        """Initializes a fhirstore.FHIRStore."""
        assert mock_fhirstore.call_count == 0
        assert mock_es_client.call_count == 0

        store = get_store()
        mock_fhirstore.assert_called_once_with(
            mock_mongo_client.return_value, mock_es_client.return_value, DB_NAME
        )
        assert store == mock_fhirstore.return_value

    def test_get_db_store_twice(self, mock_es_client, mock_mongo_client, mock_fhirstore):
        """Calling get_store twice returns the same connection."""
        assert mock_fhirstore.call_count == 0
        assert mock_es_client.call_count == 0

        store = get_store()
        mock_fhirstore.assert_called_once_with(
            mock_mongo_client.return_value, mock_es_client.return_value, DB_NAME
        )
        assert store == mock_fhirstore.return_value

        store = get_store()
        assert mock_fhirstore.call_count == 1
        assert store == mock_fhirstore.return_value
