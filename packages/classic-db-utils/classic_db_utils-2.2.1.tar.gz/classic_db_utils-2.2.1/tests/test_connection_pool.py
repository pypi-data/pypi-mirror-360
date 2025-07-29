from classic.db_utils import ConnectionPool
import pymssql
import pytest


@pytest.fixture
def connection_pool() -> ConnectionPool:
    return ConnectionPool(
        lambda: pymssql.connect(
            server='localhost',
            database='test',
            user='test',
            password='test',
        ),
        limit=1,
    )


def test_connection_pool(connection_pool: ConnectionPool):
    with connection_pool.connect() as connection:
        assert isinstance(connection, pymssql.Connection)


def test_connection_pool_limit(connection_pool: ConnectionPool):
    with connection_pool.connect() as connection:
        assert connection.reached_limit is True
