import ctypes
import os
import platform


# --- Opaque struct placeholders for GraalVM native API ---
class GraalIsolate(ctypes.Structure):
    _fields_ = []


class GraalIsolateThread(ctypes.Structure):
    _fields_ = []


class GraalIsolateParams(ctypes.Structure):
    _fields_ = []


GraalIsolate_p = ctypes.POINTER(GraalIsolate)
GraalIsolateThread_p = ctypes.POINTER(GraalIsolateThread)


class H2gisConnector:
    """
    Python wrapper for the native H2GIS library compiled with GraalVM.
    """

    def __init__(self, lib_path=None):
        """
        Initialize the H2GIS connector and create a GraalVM isolate.

        :param lib_path: Optional path to the native .so/.dll/.dylib library
        """
        if lib_path is None:
            lib_path = self._default_library_path()

        self.lib = ctypes.CDLL(lib_path)
        self._setup_c_function_signatures()

        self.isolate = GraalIsolate_p()
        self.thread = GraalIsolateThread_p()
        self.connection = 0

        params = GraalIsolateParams()
        result = self.lib.graal_create_isolate(
            ctypes.byref(params),
            ctypes.byref(self.isolate),
            ctypes.byref(self.thread)
        )
        if result != 0:
            raise RuntimeError(f"Failed to create GraalVM isolate (code {result})")

    def _default_library_path(self):
        """Find default library path relative to this file."""
        base_dir = os.path.dirname(__file__)
        system = platform.system()
        if system == "Windows":
            libname = "h2gis.dll"
        else:
            libname = "h2gis.so"

        return os.path.join(base_dir, "lib", libname)

    def _setup_c_function_signatures(self):
        """Declare argument and return types for native functions."""
        self.lib.graal_create_isolate.argtypes = [
            ctypes.POINTER(GraalIsolateParams),
            ctypes.POINTER(GraalIsolate_p),
            ctypes.POINTER(GraalIsolateThread_p),
        ]
        self.lib.graal_create_isolate.restype = ctypes.c_int

        self.lib.graal_tear_down_isolate.argtypes = [GraalIsolateThread_p]
        self.lib.graal_tear_down_isolate.restype = ctypes.c_int

        self.lib.h2gis_connect.argtypes = [
            GraalIsolateThread_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        self.lib.h2gis_connect.restype = ctypes.c_long

        self.lib.h2gis_execute_update.argtypes = [
            GraalIsolateThread_p,
            ctypes.c_long,
            ctypes.c_char_p,
        ]
        self.lib.h2gis_execute_update.restype = ctypes.c_int

        self.lib.h2gis_execute.argtypes = [
            GraalIsolateThread_p,
            ctypes.c_long,
            ctypes.c_char_p,
        ]
        self.lib.h2gis_execute.restype = ctypes.c_long

        self.lib.h2gis_fetch_row.argtypes = [
            GraalIsolateThread_p,
            ctypes.c_long,
        ]
        self.lib.h2gis_fetch_row.restype = ctypes.c_char_p

        self.lib.h2gis_close_query.argtypes = [
            GraalIsolateThread_p,
            ctypes.c_long,
        ]
        self.lib.h2gis_close_query.restype = None

        self.lib.h2gis_close_connection.argtypes = [
            GraalIsolateThread_p,
            ctypes.c_long,
        ]
        self.lib.h2gis_close_connection.restype = None

    def connect(self, db_file: str, username="sa", password=""):
        """Connect to a H2GIS database file."""
        self.connection = self.lib.h2gis_connect(
            self.thread,
            db_file.encode("utf-8"),
            username.encode("utf-8"),
            password.encode("utf-8"),
        )
        if self.connection == 0:
            raise RuntimeError("Failed to connect to H2GIS database.")

    def execute(self, sql: str) -> int:
        """Execute INSERT/UPDATE/DELETE statement and return affected row count."""
        return self.lib.h2gis_execute_update(
            self.thread,
            self.connection,
            sql.encode("utf-8"),
        )

    def fetch(self, sql: str) -> list[str]:
        """Execute SELECT statement and return list of rows."""
        handle = self.lib.h2gis_execute(
            self.thread,
            self.connection,
            sql.encode("utf-8"),
        )
        if handle == 0:
            raise RuntimeError("Query execution failed")

        rows = []
        while True:
            row = self.lib.h2gis_fetch_row(self.thread, handle)
            if not row:
                break
            rows.append(row.decode("utf-8"))

        self.lib.h2gis_close_query(self.thread, handle)
        return rows

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.lib.h2gis_close_connection(self.thread, self.connection)
            self.connection = 0

    def __del__(self):
        """Destructor to clean up isolate and resources."""
        try:
            self.close()
        except Exception:
            pass
        try:
            self.lib.graal_tear_down_isolate(self.thread)
        except Exception:
            pass
