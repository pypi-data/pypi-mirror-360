from sqlite3 import Connection as SQLite3Connection
from typing import Self

import alembic.command
import alembic.config
import alembic.migration
import alembic.script
import attrs
import sqlalchemy
import sqlalchemy.orm
import yaml
from sqlalchemy import event, Engine, create_engine, URL
from sqlalchemy.ext.asyncio import create_async_engine

from ._async_session import AsyncExperimentSession
from ._async_session import (
    GreenletSQLExperimentSession,
    ThreadedAsyncSQLExperimentSession,
)
from ._experiment_session import SQLExperimentSession
from ._serializer import SerializerProtocol
from .._session_maker import StorageManager


# We need to enable foreign key constraints for sqlite databases and not for other
# types of databases.
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


class SQLStorageManager(StorageManager):
    """Used to access experiment storage were the data are stored in a SQL database.

    This session maker can create session that connects to a database using sqlalchemy.

    This object is pickleable and can be passed to other processes, assuming that the
    database referenced by the engine is accessible from the other processes.
    In particular, in-memory sqlite databases are not accessible from other processes.

    Args:
        engine: This is used by the sessions to connect to the database.
            See sqlalchemy documentation for more information on how to create an
            engine.
        serializer: This is used to convert user defined objects to a JSON format that
            can be stored in the database.

    """

    def __init__(
        self,
        serializer: SerializerProtocol,
        engine: sqlalchemy.Engine,
        async_engine: sqlalchemy.ext.asyncio.AsyncEngine,
    ) -> None:
        self._engine = engine
        self._async_engine = async_engine
        self._session_maker = sqlalchemy.orm.sessionmaker(self._engine)
        self._async_session_maker = sqlalchemy.ext.asyncio.async_sessionmaker(
            self._async_engine
        )
        self._serializer = serializer

    def __call__(self) -> SQLExperimentSession:
        """Create a new ExperimentSession with the engine used at initialization."""

        return SQLExperimentSession(
            self._session_maker.begin(),
            self._serializer,
        )

    def async_session(self) -> AsyncExperimentSession:
        return GreenletSQLExperimentSession(
            self._async_session_maker.begin(),
            self._serializer,
        )

    # The following methods are required to make the storage manager pickleable since
    # sqlalchemy engine is not pickleable.
    # Only the engine url is pickled so the engine created upon unpickling might not be
    # exactly the same as the original one.
    def __getstate__(self):
        return {
            "url": self._engine.url,
            "async_url": self._async_engine.url,
            "serializer": self._serializer,
        }

    def __setstate__(self, state):
        engine = sqlalchemy.create_engine(state.pop("url"))
        async_engine = create_async_engine(state.pop("async_url"))
        self.__init__(state["serializer"], engine, async_engine)

    def _get_alembic_config(self) -> alembic.config.Config:
        alembic_cfg = alembic.config.Config()
        alembic_cfg.set_main_option(
            "script_location", "caqtus:session:sql:_migration:_alembic"
        )
        alembic_cfg.set_main_option(
            "sqlalchemy.url",
            self._engine.url.render_as_string(hide_password=False),
        )
        return alembic_cfg

    def check(self) -> None:
        """Check if the database is up to date with the application schema.

        Raises:
            InvalidDatabaseSchema: If the database schema is not compatible with the
                application schema.
        """

        alembic_cfg = self._get_alembic_config()

        directory = alembic.script.ScriptDirectory.from_config(alembic_cfg)

        with self._engine.begin() as connection:
            context = alembic.migration.MigrationContext.configure(connection)
            up_to_date = set(context.get_current_heads()) == set(directory.get_heads())

        if not up_to_date:
            exception = InvalidDatabaseSchemaError(
                f"Database at {self._engine.url} is not up to date."
            )
            exception.add_note(
                "Upgrade the database following the procedure at "
                "https://caqtus.readthedocs.io/en/stable/how-to/upgrade-database.html."
            )
            raise exception

    def upgrade(self) -> None:
        """Updates the database schema to the latest version.

        When called on a database already setup, this method will upgrade the database
        tables to the latest version.
        When called on an empty database, this method will create the necessary tables.

        .. Warning::

            It is strongly recommended to back up the database before running this
            method in case something goes wrong.
        """

        alembic_cfg = self._get_alembic_config()
        alembic.command.upgrade(alembic_cfg, "head")


# Deprecated alias to SQLStorageManager
SQLExperimentSessionMaker = SQLStorageManager


@attrs.define
class SQLiteConfig:
    """Configuration for connecting to a SQLite database."""

    path: str


class SQLiteStorageManager(SQLStorageManager):
    def __init__(
        self,
        serializer: SerializerProtocol,
        config: SQLiteConfig,
    ):
        path = config.path
        self.config = config
        engine = create_engine(f"sqlite:///{path}?check_same_thread=False")
        async_engine = create_async_engine(
            f"sqlite+aiosqlite:///{path}?check_same_thread=False"
        )
        super().__init__(serializer, engine, async_engine)

    def async_session(self) -> ThreadedAsyncSQLExperimentSession:
        return ThreadedAsyncSQLExperimentSession(
            self._session_maker.begin(),
            self._serializer,
        )

    def __getstate__(self):
        return {
            "serializer": self._serializer,
            "config": self.config,
        }

    def __setstate__(self, state):
        self.__init__(**state)

    def create_tables(self) -> None:
        """Create the tables in the database.

        This method is useful the first time the database is created.
        It will create missing tables and ignore existing ones.
        """

        from ._table_base import Base

        Base.metadata.create_all(self._engine)


# Deprecated alias to SQLiteStorageManager
SQLiteExperimentSessionMaker = SQLiteStorageManager


@attrs.define
class PostgreSQLConfig:
    """Configuration for connecting to a PostgreSQL database."""

    username: str
    password: str
    host: str
    port: int
    database: str

    @classmethod
    def from_file(cls, path) -> Self:
        """Create a PostgreSQLConfig from a yaml file.

        The file should contain the same keys as the attributes of this class.
        """

        with open(path) as f:
            config = yaml.safe_load(f)
        return cls(**config)


class PostgreSQLStorageManager(SQLStorageManager):
    """Used to access experiment data stored in a PostgreSQL database."""

    def __init__(
        self,
        serializer: SerializerProtocol,
        config: PostgreSQLConfig,
    ):
        sync_url = URL.create(
            "postgresql+psycopg",
            username=config.username,
            password=config.password,
            host=config.host,
            port=config.port,
            database=config.database,
        )
        engine = create_engine(sync_url, isolation_level="SERIALIZABLE")
        async_url = URL.create(
            "postgresql+psycopg",
            username=config.username,
            password=config.password,
            host=config.host,
            port=config.port,
            database=config.database,
        )
        async_engine = create_async_engine(async_url, isolation_level="SERIALIZABLE")
        self.config = config

        super().__init__(serializer, engine, async_engine)

    def async_session(self) -> ThreadedAsyncSQLExperimentSession:
        return ThreadedAsyncSQLExperimentSession(
            self._session_maker.begin(),
            self._serializer,
        )

    def __getstate__(self):
        return {
            "config": self.config,
            "serializer": self._serializer,
        }

    def __setstate__(self, state):
        config = state.pop("config")
        serializer = state.pop("serializer")
        self.__init__(serializer, config)


# Deprecated alias to PostgreSQLStorageManager
PostgreSQLExperimentSessionMaker = PostgreSQLStorageManager


class InvalidDatabaseSchemaError(Exception):
    """Raised when the database schema is not compatible with the application schema."""

    pass
