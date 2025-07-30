# classic-db-utils

Библиотека предоставляет набор утилит, облегчающих разработку компонентов,
использующих драйвера к БД напрямую.

Предоставляет классы ConnectionPool, ScopedConnection и Transaction.

## Вклад

ConnectionPool взят у Oliver Cope из проекта [Embrace](https://hg.sr.ht/~olly/embrace-sql).

## Установка

Установки с pip:

```bash
pip install classic-db-utils
```

## Использование пула соединений

```python
from classic.db_utils import ConnectionPool
import psycopg


pool = ConnectionPool(
    lambda: psycopg.connect(
        'postgres://example:example@localhost:5432/example',
    ),
    limit=1,
)


with pool.connect() as conn:
    conn.cursor().execute('SELECT 1')
```

## ScopedSession

Класс ScopedSession нужен для упрощения управления 
жизненным циклом соединений и потокобезопаностью.
Вдохновлено [sqlalchemy.ScopedSession](https://docs.sqlalchemy.org/en/20/orm/contextual.html).

Предоставляет интерфейс контекстного менеджера. При входе в контекст берет и удерживает 
соединение из пула соединений, и предоставляет доступ к атрибутам соединения.
При это ScopedSession является thread-local объектом, что означает,
что для каждого потока будет удерживаться свое соединение.

```python
from classic.db_utils import ScopedConnection

class UsersRepo:
    conn: ScopedConnection
    
    def __init__(self, conn: ScopedConnection):
        self.conn = conn
    
    def get_user(self, user_id):
        with self.conn:  # Здесь произойдет захват соединения из пула
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            return cursor.fetchone()
```

## Transaction

Класс ScopedSession нужен для упрощения управления транзакциями.
Представляет собой контекстный менеджер. На входе будет задано начало транзакции, 
при выходе будет вызван .commit у соединения, если не произошло исключение, 
или вызов .rollback, если исключение произошло.

```python
from classic.db_utils import ScopedConnection, transaction

class UsersRepo:
    conn: ScopedConnection
    
    def __init__(self, conn: ScopedConnection):
        self.conn = conn
    
    def save_user(self, user_mail: str):
        with self.conn, transaction(self.conn): 
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO users(mail) VALUES (%s)', (user_mail,))
            return cursor.fetchone()
```

## Использование с classic-operations

Ниже показан способ инвертирования зависимостей в случае,
когда логика приложения не должна зависеть от реализации слоя БД.
Логика уровня приложения завернута в operation, и в этот же инстанс 
operation добавлены ScopedConnection и Transaction.
Операция уровня приложения будут происходить в транзакции,
но в то же время логика уровня приложения не знает ничего о реализации слоя БД.

```python
from classic.components import component
from classic.db_utils import ConnectionPool, ScopedConnection, transaction
from classic.operations import Operation, operation

import psycopg


# На уровне адаптера к БД:
@component
class UsersRepo:
    conn: ScopedConnection
    
    def save_user(self, user_mail: str):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO users(mail) VALUES (%s)', (user_mail,))
        return cursor.fetchone()


# На уровне приложения:
@component
class SomeService:
    operation_: Operation
    users_repo: UsersRepo
    
    @operation
    def run(self):
        self.users_repo.save_user('some@email.com')
        self.users_repo.save_user('another@email.com')


# Композит:
pool = ConnectionPool(lambda: psycopg.connect())
conn = ScopedConnection(pool)
users_repo = UsersRepo(conn)

operation_ = Operation([conn, transaction(conn)])
SomeService(operation_, users_repo)
```
```