import unittest
from unittest.mock import MagicMock, patch
from h2gis.h2gisconnector import H2gisConnector


@patch("h2gis.h2gisconnector.ctypes.CDLL")
class TestH2gis(unittest.TestCase):
    def setUp(self):
        """
        Set up mock native library with default return values.
        This is run before each test.
        """
        self.mock_lib = MagicMock()
        self.mock_lib.graal_create_isolate.return_value = 0
        self.mock_lib.h2gis_connect.return_value = 1234
        self.mock_lib.h2gis_execute.return_value = 42
        self.mock_lib.h2gis_fetch_row.side_effect = [b"row1", b"row2", None]
        self.mock_lib.h2gis_execute_update.return_value = 1
        self.mock_lib.graal_tear_down_isolate.return_value = 0

    def _create_h2gis(self, mock_cdll):
        """
        Helper method to create H2gis instance with mocked native lib.

        @param mock_cdll: patched ctypes.CDLL
        @return: instance of H2gis
        """
        mock_cdll.return_value = self.mock_lib
        return H2gisConnector(lib_path="fake.so")

    # ------------------------
    # ✅ SUCCESS TEST CASES
    # ------------------------

    def test_connect_success(self, mock_cdll):
        """
        Test successful connection to database.
        """
        h2gis = self._create_h2gis(mock_cdll)
        h2gis.connect("/path/to/db")
        self.assertEqual(h2gis.connection, 1234)

    def test_execute_query_success(self, mock_cdll):
        """
        Test successful SELECT query with multiple rows.
        """
        h2gis = self._create_h2gis(mock_cdll)
        h2gis.connection = 1234
        result = h2gis.execute_query("SELECT * FROM my_table")
        self.assertEqual(result, ["row1", "row2"])
        self.mock_lib.h2gis_close_query.assert_called_once()

    def test_execute_update_success(self, mock_cdll):
        """
        Test successful UPDATE query with 1 row affected.
        """
        h2gis = self._create_h2gis(mock_cdll)
        h2gis.connection = 1234
        affected = h2gis.execute_update("UPDATE my_table SET x = 1")
        self.assertEqual(affected, 1)

    def test_close_connection_success(self, mock_cdll):
        """
        Test closing the connection resets the connection handle.
        """
        h2gis = self._create_h2gis(mock_cdll)
        h2gis.connection = 1234
        h2gis.close()
        self.assertEqual(h2gis.connection, 0)
        self.mock_lib.h2gis_close_connection.assert_called_once()

    # ------------------------
    # ⚠️ LIMIT TEST CASES
    # ------------------------

    def test_execute_query_empty_result(self, mock_cdll):
        """
        Test SELECT query returning no rows.
        """
        self.mock_lib.h2gis_fetch_row.side_effect = [None]
        h2gis = self._create_h2gis(mock_cdll)
        h2gis.connection = 1234
        result = h2gis.execute_query("SELECT * FROM empty_table")
        self.assertEqual(result, [])

    def test_execute_update_zero_affected(self, mock_cdll):
        """
        Test UPDATE query with 0 rows affected.
        """
        self.mock_lib.h2gis_execute_update.return_value = 0
        h2gis = self._create_h2gis(mock_cdll)
        h2gis.connection = 1234
        affected = h2gis.execute_update("DELETE FROM my_table WHERE 1=0")
        self.assertEqual(affected, 0)

    def test_close_when_not_connected(self, mock_cdll):
        """
        Test close() does nothing if already disconnected.
        """
        h2gis = self._create_h2gis(mock_cdll)
        h2gis.connection = 0
        h2gis.close()
        self.mock_lib.h2gis_close_connection.assert_not_called()

    def test_del_implicit_cleanup(self, mock_cdll):
        """
        Test that __del__ triggers close and cleanup.
        """
        h2gis = self._create_h2gis(mock_cdll)
        h2gis.connection = 1234
        del h2gis  # __del__ should be called without exception

    # ------------------------
    # ❌ ERROR TEST CASES
    # ------------------------

    def test_connect_failure(self, mock_cdll):
        """
        Test exception when connection fails (native returns 0).
        """
        self.mock_lib.h2gis_connect.return_value = 0
        h2gis = self._create_h2gis(mock_cdll)
        with self.assertRaises(RuntimeError) as ctx:
            h2gis.connect("/bad/path")
        self.assertIn("Failed to connect", str(ctx.exception))

    def test_execute_query_failure(self, mock_cdll):
        """
        Test exception if query execution fails (native returns 0).
        """
        self.mock_lib.h2gis_execute.return_value = 0
        h2gis = self._create_h2gis(mock_cdll)
        h2gis.connection = 1234
        with self.assertRaises(RuntimeError) as ctx:
            h2gis.execute_query("SELECT * FROM bad_table")
        self.assertIn("Query execution failed", str(ctx.exception))

    def test_graal_create_isolate_failure(self, mock_cdll):
        """
        Test exception if GraalVM isolate creation fails.
        """
        self.mock_lib.graal_create_isolate.return_value = 1
        mock_cdll.return_value = self.mock_lib
        with self.assertRaises(RuntimeError) as ctx:
            H2gisConnector(lib_path="fake.so")
        self.assertIn("Failed to create GraalVM isolate", str(ctx.exception))
