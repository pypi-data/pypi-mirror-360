import logging
from typing import Any, Literal, TypeVar

from polycrud import cache, exceptions
from polycrud.connectors.base import DEFAULT_CACHE_TTL, BaseConnector
from polycrud.entity.base import ModelEntity

try:
    import psycopg2
    from psycopg2 import pool
    from psycopg2.extras import RealDictCursor
except ImportError as e:
    raise ImportError("psycopg2 is not installed. Please install it with 'pip install psycopg2-binary'") from e

T = TypeVar("T", bound=ModelEntity)
P = TypeVar("P")

_Logger = logging.getLogger(__name__)


class PostgresConnector(BaseConnector):
    """
    Base class for synchronous PostgresSQL connector.
    """

    def __init__(self, host: str, port: int, user: str, password: str, db: str):
        """
        Initialize the connector with the given parameters.
        """
        self.pool: Any = None
        self.db_config: dict[str, Any] = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": db,
        }

    def connect(self, pool_name: str = "polycrud_pool", pool_size: int = 10) -> None:
        """
        Connect to the data source.
        """
        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=pool_size,
                **self.db_config
            )
            _Logger.info("Successfully connected to PostgreSQL database")
        except Exception as e:
            _Logger.error(f"Failed to connect to PostgreSQL database: {e}")
            raise exceptions.ConnectionNotInitialized(f"Failed to connect to PostgreSQL: {e}") from e

    def disconnect(self) -> None:
        """
        Disconnect from the data source.
        """
        if self.pool is not None:
            self.pool.closeall()
            self.pool = None
            _Logger.info("Successfully disconnected from PostgreSQL database")
        else:
            _Logger.warning("No active connection to disconnect")

    def health_check(self) -> bool:
        """
        Check the health of the connection.

        Returns:
            bool: True if the connection is healthy, False otherwise.
        """
        if self.pool is None:
            _Logger.warning("No connection pool initialized")
            return False

        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None and result[0] == 1
        except Exception as e:
            _Logger.error(f"Health check failed: {e}")
            return False
        finally:
            if conn:
                self.pool.putconn(conn)

    def find_one(
        self,
        collection: type[T],
        query: str | None = None,
        raise_if_not_found: bool = False,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> T | None:
        """
        Find one entity in the database.
        Args:
            collection: The schema class to use for the entity.
            query (Optional): The query string to execute.
            raise_if_not_found: Flag to raise an exception if no entity is found.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.

            **kwargs: Search by key and value pairs.

        Returns:
            A single entity of type T

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized
            EntityNotFound: If no entity is found matching the criteria
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if query:
                    # If a custom query is provided, use it with kwargs as parameters
                    cursor.execute(query, kwargs)
                else:
                    # Otherwise, build a query from kwargs
                    table_name = collection.__name__.lower()

                    # Handle the case with no search criteria
                    if not kwargs:
                        query = f"SELECT * FROM {table_name} LIMIT 1"
                        cursor.execute(query)
                    else:
                        # Build WHERE clause from kwargs
                        where_conditions = " AND ".join([f"{key} = %s" for key in kwargs])
                        query = f"SELECT * FROM {table_name} WHERE {where_conditions} LIMIT 1"
                        cursor.execute(query, list(kwargs.values()))

                result = cursor.fetchone()

                if not result:
                    if raise_if_not_found:
                        raise exceptions.NotFoundError(f"Entity not found in {collection.__name__}")
                    return None

                # Create an instance of the collection class with the result
                return collection(**dict(result))

        except psycopg2.Error as e:
            _Logger.error(f"Database error in find_one: {e}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)

    def find_many(
        self,
        collection: type[T],
        *,
        limit: int = 10_000,
        offset: int = 0,
        sort_field: str = "id",
        sort_dir: Literal["asc", "desc"] = "asc",
        query: str | None = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> list[T]:
        """
        Find multiple entities in the database.

        Args:
            collection: The schema class to use for the entities.
            limit: Maximum number of results to return.
            offset: Offset for pagination.
            sort_field: Field to sort by.
            sort_dir: Sort direction ('asc' or 'desc').
            query: Optional custom query string to execute.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.
            **kwargs: Search by key and value pairs.

        Returns:
            A list of entities of type T

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if query:
                    # If a custom query is provided, use it with kwargs as parameters
                    # Note: Custom queries should handle pagination and sorting themselves
                    cursor.execute(query, kwargs)
                else:
                    # Otherwise, build a query from kwargs
                    table_name = collection.__name__.lower()

                    # Build the base query
                    base_query = f"SELECT * FROM {table_name}"

                    params = []
                    # Build WHERE clause from kwargs if any
                    if kwargs:
                        where_conditions = " AND ".join([f"{key} = %s" for key in kwargs])
                        base_query += f" WHERE {where_conditions}"
                        params.extend(list(kwargs.values()))

                    # Add sorting
                    base_query += f" ORDER BY {sort_field} {sort_dir.upper()}"

                    # Add pagination
                    base_query += " LIMIT %s OFFSET %s"
                    params.extend([limit, offset])

                    # Execute the query
                    cursor.execute(base_query, params)

                results = cursor.fetchall()

                # Create instances of the collection class with the results
                return [collection(**dict(row)) for row in results]

        except psycopg2.Error as e:
            _Logger.error(f"Database error in find_many: {e}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)

    @cache.cache()
    def insert_one(
        self,
        obj: T,
        *,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> T:
        """
        Insert a single entity into the database.

        Args:
            obj: The entity object to insert.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.

        Returns:
            The inserted entity with updated fields (like auto-generated ID).

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized.
            InsertionError: If the insertion operation fails.
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        if not isinstance(obj, ModelEntity):
            raise ValueError("Object must be an instance of ModelEntity")

        # Get the table name from the object's class name
        table_name = obj.__class__.__name__.lower()

        # Convert the object to a dictionary
        data = obj.dict()

        # Remove None values from the data dictionary
        data = {k: v for k, v in data.items() if v is not None}

        # Prepare the fields and placeholders for the INSERT statement
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        values = list(data.values())

        query = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"

        # Add RETURNING clause to get the inserted ID
        if hasattr(obj, "id") and obj.id is None:
            query += " RETURNING id"

        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute(query, values)

                # Get the inserted ID if there's an auto-increment field
                if hasattr(obj, "id") and obj.id is None:
                    result = cursor.fetchone()
                    if result:
                        obj.id = result[0]

                conn.commit()
                _Logger.info(f"Successfully inserted entity into {table_name}")
                return obj

        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            _Logger.error(f"Error inserting entity: {e}")
            raise exceptions.InsertionError(f"Failed to insert entity: {e}") from e
        finally:
            if conn:
                self.pool.putconn(conn)

    @cache.cache()
    def insert_many(
        self,
        objs: list[T],
        *,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> list[T]:
        """
        Insert multiple entities into the database.

        Args:
            objs: A list of entity objects to insert.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.

        Returns:
            The inserted entities with updated fields (like auto-generated ID).

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized.
            InsertionError: If the insertion operation fails.
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        if not all(isinstance(o, ModelEntity) for o in objs):
            raise ValueError("All objects must be instances of ModelEntity")

        # Get the table name from the first object's class name
        table_name = objs[0].__class__.__name__.lower()

        # Convert the objects to a list of dictionaries
        data_list = [o.dict() for o in objs]

        # Remove None values from each data dictionary
        data_list = [{k: v for k, v in data.items() if v is not None} for data in data_list]

        # Prepare the fields and placeholders for the INSERT statement
        fields = ", ".join(data_list[0].keys())
        placeholders = ", ".join(["%s"] * len(data_list[0]))
        values = [tuple(data.values()) for data in data_list]

        query = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"

        # Add RETURNING clause to get the inserted IDs
        if hasattr(objs[0], "id") and objs[0].id is None:
            query += " RETURNING id"

        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor() as cursor:
                # Use execute_values for better performance with multiple inserts
                from psycopg2.extras import execute_values

                if hasattr(objs[0], "id") and objs[0].id is None:
                    # Use RETURNING to get the inserted IDs
                    template = f"({placeholders})"
                    result = execute_values(
                        cursor,
                        f"INSERT INTO {table_name} ({fields}) VALUES %s RETURNING id",
                        values,
                        template=template,
                        fetch=True
                    )
                    # Update the objects with their new IDs
                    for i, obj in enumerate(objs):
                        if i < len(result):
                            obj.id = result[i][0]
                else:
                    execute_values(cursor, query, values)

                conn.commit()
                _Logger.info(f"Successfully inserted entities into {table_name}")
                return objs

        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            _Logger.error(f"Error inserting entities: {e}")
            raise exceptions.InsertionError(f"Failed to insert entities: {e}") from e
        finally:
            if conn:
                self.pool.putconn(conn)

    @cache.cache()
    def update_one(
        self,
        obj: T,
        *,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> T:
        """
        Update a single entity in the database.

        Args:
            obj: The entity object to update.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.

        Returns:
            The updated entity.

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized.
            UpdateError: If the update operation fails.
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        if not isinstance(obj, ModelEntity):
            raise ValueError("Object must be an instance of ModelEntity")

        # Get the table name from the object's class name
        table_name = obj.__class__.__name__.lower()

        # Convert the object to a dictionary
        data = obj.dict()

        # Remove None values from the data dictionary
        data = {k: v for k, v in data.items() if v is not None}

        # Prepare the fields and placeholders for the UPDATE statement
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        values = list(data.values())

        # Add the ID to the end of the values list for the WHERE clause
        where_clause = "id = %s"
        values.append(obj.id)

        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
                _Logger.info(f"Successfully updated entity in {table_name}")
                return obj

        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            _Logger.error(f"Error updating entity: {e}")
            raise exceptions.UpdateError(f"Failed to update entity: {e}") from e
        finally:
            if conn:
                self.pool.putconn(conn)

    @cache.cache()
    def delete_one(self, collection: type[T], *, id: int, _use_cache: bool | None = None, _cache_ttl: int = DEFAULT_CACHE_TTL) -> None:
        """
        Delete a single entity from the database.

        Args:
            collection: The schema class to use for the entity.
            id: The ID of the entity to delete.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized.
            DeletionError: If the deletion operation fails.
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor() as cursor:
                table_name = collection.__name__.lower()
                query = f"DELETE FROM {table_name} WHERE id = %s"
                cursor.execute(query, (id,))
                conn.commit()
                _Logger.info(f"Successfully deleted entity from {table_name}")

        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            _Logger.error(f"Error deleting entity: {e}")
            raise exceptions.DeletionError(f"Failed to delete entity: {e}") from e
        finally:
            if conn:
                self.pool.putconn(conn)

    @cache.cache()
    def delete_many(
        self,
        collection: type[T],
        *,
        ids: list[int],
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> None:
        """
        Delete multiple entities from the database.

        Args:
            collection: The schema class to use for the entities.
            ids: A list of IDs of the entities to delete.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized.
            DeletionError: If the deletion operation fails.
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor() as cursor:
                table_name = collection.__name__.lower()
                # Use ANY() operator for PostgreSQL IN clause
                query = f"DELETE FROM {table_name} WHERE id = ANY(%s)"
                cursor.execute(query, (ids,))
                conn.commit()
                _Logger.info(f"Successfully deleted entities from {table_name}")

        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            _Logger.error(f"Error deleting entities: {e}")
            raise exceptions.DeletionError(f"Failed to delete entities: {e}") from e
        finally:
            if conn:
                self.pool.putconn(conn)

    @cache.cache()
    def count(
        self,
        collection: type[T],
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> int:
        """
        Count the number of entities in the database.

        Args:
            collection: The schema class to use for the entities.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.
            **kwargs: Search by key and value pairs.

        Returns:
            The count of entities of type T

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor() as cursor:
                table_name = collection.__name__.lower()

                # Build base query
                query = f"SELECT COUNT(*) FROM {table_name}"

                params = []
                # Add WHERE clause if kwargs are provided
                if kwargs:
                    where_conditions = " AND ".join([f"{key} = %s" for key in kwargs])
                    query += f" WHERE {where_conditions}"
                    params = list(kwargs.values())

                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result else 0

        except psycopg2.Error as e:
            _Logger.error(f"Database error in count: {e}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)

    @cache.cache()
    def raw_query(
        self,
        query: str,
        params: list[Any] | None = None,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> Any:
        """
        Execute a raw SQL query.

        Args:
            query: The SQL query string.
            params: Optional parameters for the query.
            _use_cache: Optional flag to use cache.
            _cache_ttl: Optional cache TTL in seconds.
            _override_cache_key: Optional cache key to override the default.

        Returns:
            A list of dictionaries representing the rows returned by the query.

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized
            QueryError: If the query execution fails
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return [dict(row) for row in result]

        except psycopg2.Error as e:
            _Logger.error(f"Database error in raw_query: {e}")
            raise exceptions.QueryExecutionError(f"Failed to execute raw query: {e}") from e
        finally:
            if conn:
                self.pool.putconn(conn)
