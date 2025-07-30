from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Any, Optional, ClassVar, Generator, Type, Dict

from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
    ConfigDict,
)
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import url as sqlalchemy_url
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool, StaticPool

# Assuming these are your project's internal modules
from sibi_dst.utils import Logger
from ._sql_model_builder import SqlAlchemyModelBuilder


class SqlAlchemyConnectionConfig(BaseModel):
    """
    A thread-safe, registry-backed SQLAlchemy connection manager.

    This class encapsulates database connection configuration and provides robust,
    shared resource management. It is designed to be used as a context manager
    to ensure resources are always released correctly.

    Recommended Usage is via the `with` statement.
    with SqlAlchemyConnectionConfig(...) as config:
        session = config.get_session()
        # ... do work ...
    # config.close() is called automatically upon exiting the block.

    Key Features:
      - Context Manager Support: Guarantees resource cleanup.
      - Shared Engine & Pool: Reuses a single SQLAlchemy Engine for identical
        database URLs and pool settings, improving application performance.
      - Reference Counting: Safely manages the lifecycle of the shared engine,
        disposing of it only when the last user has closed its connection config.
    """
    # --- Public Configuration ---
    connection_url: str
    table: Optional[str] = None
    debug: bool = False

    # --- Pool Configuration ---
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 1800
    pool_pre_ping: bool = True
    poolclass: Type[QueuePool] = QueuePool

    # --- Internal & Runtime State ---
    model: Optional[Type[Any]] = None
    engine: Optional[Engine] = None
    logger: Optional[Logger] = None
    session_factory: Optional[sessionmaker] = None

    # --- Private State ---
    _engine_key_instance: tuple = ()
    _closed: bool = False  # Flag to prevent double-closing.

    # --- Class-level Shared Resources ---
    _engine_registry: ClassVar[Dict[tuple, Dict[str, Any]]] = {}
    _registry_lock: ClassVar[threading.Lock] = threading.Lock()

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Add __enter__ and __exit__ for context manager protocol
    def __enter__(self) -> SqlAlchemyConnectionConfig:
        """Enter the runtime context, returning self."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the runtime context, ensuring that close() is called."""
        self.close()

    @field_validator("pool_size", "max_overflow", "pool_timeout", "pool_recycle")
    @classmethod
    def _validate_pool_params(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Pool parameters must be non-negative")
        return v

    @model_validator(mode="after")
    def _init_all(self) -> SqlAlchemyConnectionConfig:
        """Orchestrates the initialization process after Pydantic validation."""
        self._init_logger()
        self._engine_key_instance = self._get_engine_key()
        self._init_engine()
        self._validate_conn()
        self._build_model()
        if self.engine:
            self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        return self

    def _init_logger(self) -> None:
        """Initializes the logger for this instance."""
        if self.logger is None:
            self.logger = Logger.default_logger(logger_name=self.__class__.__name__)
        log_level = Logger.DEBUG if self.debug else Logger.INFO
        self.logger.set_level(log_level)

    def _get_engine_key(self) -> tuple:
        """Generates a unique, normalized key for an engine configuration."""
        parsed = sqlalchemy_url.make_url(self.connection_url)
        query = {k: v for k, v in parsed.query.items() if not k.startswith("pool_")}
        normalized_url = parsed.set(query=query)
        key_parts = [str(normalized_url)]
        if self.poolclass not in (NullPool, StaticPool):
            key_parts += [
                self.pool_size, self.max_overflow, self.pool_timeout,
                self.pool_recycle, self.pool_pre_ping
            ]
        return tuple(key_parts)

    def _init_engine(self) -> None:
        """Initializes or reuses a shared SQLAlchemy Engine."""
        with self._registry_lock:
            engine_wrapper = self._engine_registry.get(self._engine_key_instance)
            if engine_wrapper:
                self.engine = engine_wrapper['engine']
                engine_wrapper['ref_count'] += 1
                self.logger.debug(f"Reusing engine. Ref count: {engine_wrapper['ref_count']}.")
            else:
                self.logger.debug(f"Creating new engine for key: {self._engine_key_instance}")
                try:
                    new_engine = create_engine(
                        self.connection_url, pool_size=self.pool_size,
                        max_overflow=self.max_overflow, pool_timeout=self.pool_timeout,
                        pool_recycle=self.pool_recycle, pool_pre_ping=self.pool_pre_ping,
                        poolclass=self.poolclass,
                    )
                    self.engine = new_engine
                    self._attach_events()
                    self._engine_registry[self._engine_key_instance] = {
                        'engine': new_engine, 'ref_count': 1, 'active_connections': 0
                    }
                except Exception as e:
                    self.logger.error(f"Failed to create engine: {e}")
                    raise SQLAlchemyError(f"Engine creation failed: {e}") from e

    def close(self) -> None:
        """
        Decrements the engine's reference count and disposes of the engine
        if the count reaches zero. This is now typically called automatically
        when exiting a `with` block.
        """
        # Prevent the method from running more than once per instance.
        if self._closed:
            self.logger.debug("Attempted to close an already-closed config instance.")
            return

        with self._registry_lock:
            key = self._engine_key_instance
            engine_wrapper = self._engine_registry.get(key)

            if not engine_wrapper:
                self.logger.warning("Attempted to close a config whose engine is not in the registry.")
                return

            engine_wrapper['ref_count'] -= 1
            self.logger.debug(f"Closing config. Ref count is now {engine_wrapper['ref_count']}.")

            if engine_wrapper['ref_count'] <= 0:
                self.logger.debug(f"Disposing engine as reference count is zero. Key: {key}")
                engine_wrapper['engine'].dispose()
                del self._engine_registry[key]

        # Mark this instance as closed to prevent subsequent calls.
        self._closed = True

    # ... (the rest of your methods like _attach_events, _on_checkout, get_session, etc. remain unchanged)
    # They are omitted here for brevity but should be included in your final file.

    def _attach_events(self) -> None:
        """Attaches checkout/checkin events to the engine for connection tracking."""
        if self.engine:
            event.listen(self.engine, "checkout", self._on_checkout)
            event.listen(self.engine, "checkin", self._on_checkin)

    def _on_checkout(self, *args) -> None:
        """Event listener for when a connection is checked out from the pool."""
        with self._registry_lock:
            wrapper = self._engine_registry.get(self._engine_key_instance)
            if wrapper:
                wrapper['active_connections'] += 1
        self.logger.debug(f"Connection checked out. Active: {self.active_connections}")

    def _on_checkin(self, *args) -> None:
        """Event listener for when a connection is returned to the pool."""
        with self._registry_lock:
            wrapper = self._engine_registry.get(self._engine_key_instance)
            if wrapper:
                wrapper['active_connections'] = max(0, wrapper['active_connections'] - 1)
        self.logger.debug(f"Connection checked in. Active: {self.active_connections}")

    @property
    def active_connections(self) -> int:
        """Returns the number of active connections for this instance's engine."""
        with self._registry_lock:
            wrapper = self._engine_registry.get(self._engine_key_instance)
            return wrapper['active_connections'] if wrapper else 0

    def _validate_conn(self) -> None:
        """Tests the database connection by executing a simple query."""
        try:
            with self.managed_connection() as conn:
                conn.execute(text("SELECT 1"))
            self.logger.debug("Database connection validated successfully.")
        except OperationalError as e:
            self.logger.error(f"Database connection failed: {e}")
            raise ValueError(f"DB connection failed: {e}") from e

    @contextmanager
    def managed_connection(self) -> Generator[Any, None, None]:
        """Provides a single database connection from the engine pool."""
        if not self.engine:
            raise RuntimeError("Engine not initialized. Cannot get a connection.")
        conn = self.engine.connect()
        try:
            yield conn
        finally:
            conn.close()

    def get_session(self) -> Session:
        """Returns a new SQLAlchemy Session from the session factory."""
        if not self.session_factory:
            raise RuntimeError("Session factory not initialized. Cannot get a session.")
        return self.session_factory()

    def _build_model(self) -> None:
        """Dynamically builds an ORM model if `self.table` is set."""
        if not self.table or not self.engine:
            return
        try:
            builder = SqlAlchemyModelBuilder(self.engine, self.table)
            self.model = builder.build_model()
            self.logger.debug(f"Successfully built ORM model for table: {self.table}")
        except Exception as e:
            self.logger.error(f"Failed to build ORM model for table '{self.table}': {e}")
            raise ValueError(f"Model construction failed for table '{self.table}': {e}") from e
