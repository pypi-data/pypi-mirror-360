from psycopg2 import connect
from psycopg2.errors import ConnectionException, ConnectionFailure


class PostreSQLConnector:
    def __init__(self, host: str, password: str = None, database: str = "db") -> None:
        self._host = host
        assert type(host) is str
        "host must be a str containing postgresql app name"
        self._password = password
        self._database = database
        self.connect()

    def connect(self):
        while True:
            try:
                self._postgresql_client = connect(
                    database=self._database,
                    host=self._host,
                    user="admin",
                    password=self._password,
                )
                print(f"Connected to PostgreSQL ({self._database}): {self._host}")
                break
            except (
                ConnectionException,
                ConnectionFailure,
            ) as e:
                print(f"PostgreSQL connection error: {e}")
                print(f"retrying to connect...")

    def get_postgresql_client(self):
        return self._postgresql_client


def get_postgresql_access(
    app_name: str, password: str, database: str = "db", restart: bool = False
):
    global _postgresql_access

    def init_access():
        global _postgresql_access
        _postgresql_access = PostreSQLConnector(
            host=app_name, password=password, database=database
        )

    try:
        if not isinstance(_postgresql_access, PostreSQLConnector) or restart:
            init_access()
    except NameError:
        init_access()
        pass
    return _postgresql_access
