import logging
from typing import Any, Literal, TypeVar

from polycrud import acache, exceptions
from polycrud.connectors.base import DEFAULT_CACHE_TTL, AsyncBaseConnector
from polycrud.entity.base import ModelEntity

try:
    import aiomysql
except ImportError as e:
    raise ImportError("aiomysql is not installed. Please install it using 'pip install aiomysql'.") from e

T = TypeVar("T", bound=ModelEntity)
P = TypeVar("P")

_Logger = logging.getLogger(__name__)


class AsyncMySQLConnector(AsyncBaseConnector):
    """
    Base class for all connectors.
    """

    def __init__(self, host: str, port: int, user: str, password: str, db: str):
        """
        Initialize the connector with the given parameters.
        """
        self.pool: Any = None
        self.db_config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "db": db,
        }

    async def connect(self, minsize: int = 1, maxsize: int = 10) -> None:
        """
        Connect to the data source.
        """
        try:
            self.pool = await aiomysql.create_pool(minsize=minsize, maxsize=maxsize, autocommit=True, **self.db_config)
            _Logger.info("Successfully connected to MySQL database")
        except Exception as e:
            _Logger.error(f"Failed to connect to MySQL database: {e}")
            raise exceptions.ConnectionNotInitialized(f"Failed to connect to MySQL: {e}") from e

    async def disconnect(self) -> None:
        """
        Disconnect from the data source.
        """
        if self.pool is not None:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
            _Logger.info("Successfully disconnected from MySQL database")
        else:
            _Logger.warning("No active connection to disconnect")

    async def health_check(self) -> bool:
        """
        Check the health of the connection.

        Returns:
            bool: True if the connection is healthy, False otherwise.
        """
        if self.pool is None:
            _Logger.warning("No connection pool initialized")
            return False

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    result = await cursor.fetchone()
                    return result is not None and result[0] == 1
        except Exception as e:
            _Logger.error(f"Health check failed: {e}")
            return False

    @acache.cache()
    async def find_one(
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
            raise_if_not_found: Whether to raise an exception if not found.
            _use_cache: Whether to use the cache.
            _cache_ttl: Cache time-to-live in seconds.
            _override_cache_key: Cache key to override the default.
            **kwargs: Search by key and value pairs.

        Returns:
            A single entity of type T

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized
            EntityNotFound: If no entity is found matching the criteria
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    if query:
                        # If a custom query is provided, use it with kwargs as parameters
                        await cursor.execute(query, kwargs)
                    else:
                        # Otherwise, build a query from kwargs
                        table_name = collection.__name__.lower()

                        # Handle the case with no search criteria
                        if not kwargs:
                            query = f"SELECT * FROM {table_name} LIMIT 1"
                            await cursor.execute(query)
                        else:
                            # Build WHERE clause from kwargs
                            where_conditions = " AND ".join([f"{key} = %s" for key in kwargs])
                            query = f"SELECT * FROM {table_name} WHERE {where_conditions} LIMIT 1"
                            await cursor.execute(query, list(kwargs.values()))

                    result = await cursor.fetchone()

                    if not result:
                        if raise_if_not_found:
                            raise exceptions.NotFoundError(f"Entity not found in {collection.__name__}")
                        return None
                    # Create an instance of the collection class with the result
                    return collection(**result)

                except aiomysql.Error as e:
                    logging.error(f"Database error in find_one: {e}")
                    raise

    @acache.cache()
    async def find_many(
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
            offset:
            sort_field: Field to sort by.
            sort_dir: Sort direction ('asc' or 'desc').
            query: Optional custom query string to execute.
            _use_cache: Whether to use the cache.
            _cache_ttl: Cache time-to-live in seconds.
            _override_cache_key: Cache key to override the default.
            **kwargs: Search by key and value pairs.

        Returns:
            A list of entities of type T

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    if query:
                        # If a custom query is provided, use it with kwargs as parameters
                        # Note: Custom queries should handle pagination and sorting themselves
                        await cursor.execute(query, kwargs)
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
                        await cursor.execute(base_query, params)

                    results = await cursor.fetchall()

                    # Create instances of the collection class with the results
                    return [collection(**row) for row in results]

                except aiomysql.Error as e:
                    _Logger.error(f"Database error in find_many: {e}")
                    raise

    @acache.cache()
    async def insert_one(
        self, obj: T, _use_cache: bool | None = None, _cache_ttl: int = DEFAULT_CACHE_TTL, _override_cache_key: str | None = None
    ) -> T:
        """
        Insert a single entity into the database.

        Args:
            obj: The entity object to insert.
            _use_cache: Whether to use the cache.
            _cache_ttl: Cache time-to-live in seconds.
            _override_cache_key: Cache key to override the default.

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

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(query, values)

                    # Get the last inserted ID if there's an auto-increment field
                    if hasattr(obj, "id") and obj.id is None:
                        # Get the inserted ID
                        obj.id = cursor.lastrowid

                    _Logger.info(f"Successfully inserted entity into {table_name}")
                    return obj

                except aiomysql.Error as e:
                    _Logger.error(f"Error inserting entity: {e}")
                    raise exceptions.InsertionError(f"Failed to insert entity: {e}") from e

    @acache.cache()
    async def insert_many(
        self, objs: list[T], _use_cache: bool | None = None, _cache_ttl: int = DEFAULT_CACHE_TTL, _override_cache_key: str | None = None
    ) -> list[T]:
        """
        Insert multiple entities into the database.

        Args:
            objs: A list of entity objects to insert.
            _use_cache: Whether to use the cache.
            _cache_ttl: Cache time-to-live in seconds.
            _override_cache_key: Cache key to override the default.

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

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.executemany(query, values)

                    # Get the last inserted ID if there's an auto-increment field
                    if hasattr(objs[0], "id") and objs[0].id is None:
                        # Get the inserted IDs
                        for i, o in enumerate(objs):
                            o.id = cursor.lastrowid + i

                    _Logger.info(f"Successfully inserted entities into {table_name}")
                    return objs

                except aiomysql.Error as e:
                    _Logger.error(f"Error inserting entities: {e}")
                    raise exceptions.InsertionError(f"Failed to insert entities: {e}") from e

    @acache.cache()
    async def update_one(
        self, obj: T, _use_cache: bool | None = None, _cache_ttl: int = DEFAULT_CACHE_TTL, _override_cache_key: str | None = None
    ) -> T:
        """
        Update a single entity in the database.

        Args:
            obj: The entity object to update.
            _use_cache: Whether to use the cache.
            _cache_ttl: Cache time-to-live in seconds.
            _override_cache_key: Cache key to override the default.

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
        data = obj.model_dump()

        # Remove None values from the data dictionary
        data = {k: v for k, v in data.items() if v is not None}

        # Prepare the fields and placeholders for the UPDATE statement
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        values = list(data.values())

        # Add the ID to the end of the values list for the WHERE clause
        where_clause = "id = %s"
        values.append(obj.id)

        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(query, values)
                    _Logger.info(f"Successfully updated entity in {table_name}")
                    return obj

                except aiomysql.Error as e:
                    _Logger.error(f"Error updating entity: {e}")
                    raise exceptions.UpdateError(f"Failed to update entity: {e}") from e

    @acache.cache()
    async def delete_one(
        self,
        collection: type[T],
        *,
        id: int,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> None:
        """
        Delete a single entity from the database.

        Args:
            collection: The schema class to use for the entity.
            id: The ID of the entity to delete.
            _use_cache: Whether to use the cache.
            _cache_ttl: Cache time-to-live in seconds.
            _override_cache_key: Cache key to override the default.

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized.
            DeletionError: If the deletion operation fails.
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    table_name = collection.__name__.lower()
                    query = f"DELETE FROM {table_name} WHERE id = %s"
                    await cursor.execute(query, (id,))
                    _Logger.info(f"Successfully deleted entity from {table_name}")

                except aiomysql.Error as e:
                    _Logger.error(f"Error deleting entity: {e}")
                    raise exceptions.DeletionError(f"Failed to delete entity: {e}") from e

    @acache.cache()
    async def delete_many(
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
            _use_cache: Whether to use the cache.
            _cache_ttl: Cache time-to-live in seconds.
            _override_cache_key: Cache key to override the default.

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized.
            DeletionError: If the deletion operation fails.
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    table_name = collection.__name__.lower()
                    query = f"DELETE FROM {table_name} WHERE id IN %s"
                    await cursor.execute(query, (tuple(ids),))
                    _Logger.info(f"Successfully deleted entities from {table_name}")

                except aiomysql.Error as e:
                    _Logger.error(f"Error deleting entities: {e}")
                    raise exceptions.DeletionError(f"Failed to delete entities: {e}") from e

    @acache.cache()
    async def count(
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
            _use_cache: Whether to use the cache.
            _cache_ttl: Cache time-to-live in seconds.
            _override_cache_key: Cache key to override the default.
            **kwargs: Search by key and value pairs.

        Returns:
            The count of entities of type T

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    table_name = collection.__name__.lower()
                    where_conditions = " AND ".join([f"{key} = %s" for key in kwargs])
                    query = f"SELECT COUNT(*) FROM {table_name} WHERE {where_conditions}"
                    await cursor.execute(query, list(kwargs.values()))
                    result = await cursor.fetchone()
                    return result[0] if result else 0
                except aiomysql.Error as e:
                    _Logger.error(f"Database error in count: {e}")
                    raise

    @acache.cache()
    async def aggregate(
        self,
        collection: type[T],
        aggregate_func: str,
        field: str,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Perform an aggregation operation on the database.

        Args:
            collection: The schema class to use for the entities.
            aggregate_func: The aggregation function to use (e.g., 'SUM', 'AVG').
            field: The field to apply the aggregation function on.
            _use_cache: Whether to use the cache.
            _cache_ttl: Cache time-to-live in seconds.
            _override_cache_key: Cache key to override the default.
            **kwargs: Search by key and value pairs.

        Returns:
            The result of the aggregation operation.

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    table_name = collection.__name__.lower()
                    where_conditions = " AND ".join([f"{key} = %s" for key in kwargs])
                    query = f"SELECT {aggregate_func}({field}) FROM {table_name} WHERE {where_conditions}"
                    await cursor.execute(query, list(kwargs.values()))
                    result = await cursor.fetchone()
                    return result[0] if result else None
                except aiomysql.Error as e:
                    _Logger.error(f"Database error in aggregate: {e}")
                    raise exceptions.AggregationError(f"Failed to perform aggregation: {e}") from e

    @acache.cache()
    async def raw_query(
        self,
        query: str,
        *args: Any,
        _use_cache: bool | None = None,
        _cache_ttl: int = DEFAULT_CACHE_TTL,
        _override_cache_key: str | None = None,
    ) -> Any:
        """
        Execute a raw SQL query.

        Args:
            query: The SQL query string to execute.
            *args: Parameters for the SQL query.
            _use_cache: Whether to use the cache.
            _cache_ttl: Cache time-to-live in seconds.
            _override_cache_key: Cache key to override the default.

        Returns:
            The result of the query execution.

        Raises:
            ConnectionNotInitialized: If the connection pool is not initialized
            QueryExecutionError: If the query execution fails.
        """
        if self.pool is None:
            raise exceptions.ConnectionNotInitialized("Database connection not initialized")

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    await cursor.execute(query, args)
                    result = await cursor.fetchall()
                    return result
                except aiomysql.Error as e:
                    _Logger.error(f"Error executing raw query: {e}")
                    raise exceptions.QueryExecutionError(f"Failed to execute raw query: {e}") from e
