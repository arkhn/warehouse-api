
from db import get_db_connection, reset_db_connection

from unittest import TestCase
from unittest.mock import Mock, patch


@patch('fhirbase.FHIRBase')
@patch('psycopg2.connect')
class TestDB(TestCase):

    def tearDown(self):
        reset_db_connection()

    def test_get_db_connection_once(
            self, mock_psycopg2_connect, mock_FHIRBASE):
        """Calls psycopg2.connect and instantiate a Fhirbase object."""
        assert mock_psycopg2_connect.call_count == 0
        assert mock_FHIRBASE.call_count == 0

        fb = get_db_connection()
        assert mock_psycopg2_connect.call_count == 1
        assert mock_FHIRBASE.call_count == 1
        assert fb == mock_FHIRBASE.return_value

    def test_get_db_connection_twice(
            self, mock_psycopg2_connect, mock_FHIRBASE):
        """Calling get_db_connection twice returns the same connection."""
        assert mock_psycopg2_connect.call_count == 0
        assert mock_FHIRBASE.call_count == 0

        fb = get_db_connection()
        assert mock_psycopg2_connect.call_count == 1
        assert mock_FHIRBASE.call_count == 1
        assert fb == mock_FHIRBASE.return_value

        fb = get_db_connection()
        assert mock_psycopg2_connect.call_count == 1
        assert mock_FHIRBASE.call_count == 1
        assert fb == mock_FHIRBASE.return_value
