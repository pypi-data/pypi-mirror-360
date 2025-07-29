import threading
from typing import  Any

from .pool import ConnectionPool


class ScopedConnection(threading.local):
    _conn_pool: ConnectionPool

    def __init__(self, conn_pool: ConnectionPool):
        super().__init__()
        self._conn_pool = conn_pool

    def __enter__(self):
        self._conn = self._conn_pool.getconn()
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool | None:
        self._conn_pool.release(self._conn)
        del self._conn
        return False

    def __getattr__(self, item: str) -> Any:
        return getattr(self._conn, item)

    def __module__(self) -> str:
        return self._conn.__module__


class Transaction:

    def __init__(self, conn):
        self._conn = conn

    def __enter__(self):
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool | None:
        if exc_type:
            self._conn.rollback()
        else:
            self._conn.commit()

        return False
