import dataclasses
from functools import wraps
from typing import Optional, Type, Any
from unittest.mock import MagicMock

import pytest
import psycopg

from classic.components import component, doublewrap
from classic.db_utils import ConnectionPool, ScopedConnection, Transaction, transaction
from classic.operations import Operation, operation


@doublewrap
def scenario(fn, prop: str, cls: Type[Any]):

    @wraps
    def wrapper(obj, **kwargs):
        setattr(obj, prop, cls(**kwargs))
        return fn(obj)

    return wrapper


@component
class SomeClass:
    conn: ScopedConnection
    op: Operation

    def method_1(self):
        with self.conn:
            return 1

    def method_2(self):
        with self.conn, Transaction(self.conn):
            return 1

    @operation(prop='op_conn')
    def method_3(self):
        with Transaction(self.conn):
            return 1

    @operation(prop='op_tx')
    def method_4(self):
        return 1


@component
class SomeUseCase:
    conn: ScopedConnection
    op: Operation

    @dataclasses.dataclass
    class Params:
        prop_1: Optional[str] = None
        prop_2: Optional[str] = None

    params: Params = None

    @operation
    @scenario(Params)
    def run(self):
        self.op.on_finish(self._clear_self)

    def _clear_self(self):
        self.prop_1 = None
        self.prop_2 = None


pool = ConnectionPool(lambda: psycopg.connect())
conn = ScopedConnection(pool)
op = Operation([conn, transaction(conn)])
SomeClass(op=op)


def test_decorator_with_custom_names(some_class_obj):
    result = some_class_obj.custom_method()

    assert result == 'custom_connection'
    some_class_obj.my_connect.assert_called_once()
