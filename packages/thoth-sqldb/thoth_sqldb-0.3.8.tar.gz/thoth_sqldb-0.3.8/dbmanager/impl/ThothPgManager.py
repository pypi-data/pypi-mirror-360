import os
import logging
from threading import Lock
from typing import Any, Dict, List, Optional, Union, Type, TypeVar


from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from tabulate import tabulate

from ..ThothDbManager import ThothDbManager

T = TypeVar('T', bound='ThothPgManager')

class ThothPgManager(ThothDbManager):
    """
    PostgreSQL implementation of ThothDbManager.
    """
    _instances = {}
    _lock = Lock()

    @classmethod
    def get_instance(cls: Type[T], 
                    host: str, 
                    port: int, 
                    dbname: str, 
                    user: str, 
                    password: str, 
                    db_root_path: str, 
                    db_mode: str = "dev", 
                    schema: str = "public",
                    language: str = "English",
                    **kwargs) -> T:
        """
        Get or create a singleton instance based on connection parameters.
        
        Args:
            host (str): Database host.
            port (int): Database port.
            dbname (str): Database name.
            user (str): Database user.
            password (str): Database password.
            db_root_path (str): Path to the database root directory.
            db_mode (str, optional): Database mode (dev, prod, etc.). Defaults to "dev".
            schema (str, optional): Database schema. Defaults to "public".
            **kwargs: Additional parameters.
            
        Returns:
            ThothPgManager: An instance of the PostgreSQL manager.
            
        Raises:
            ValueError: If required parameters are missing.
            TypeError: If parameters have incorrect types.
            :param schema:
            :param db_mode:
            :param password:
            :type db_root_path: object
            :param user:
            :param dbname:
            :param port:
            :param host:
            :param language:
        """
        required_params = ['host', 'port', 'dbname', 'user', 'password', 'db_root_path','language']

        # Create a dictionary with all parameters
        all_params = {
            'host': host,
            'port': port,
            'dbname': dbname,
            'user': user,
            'password': password,
            'db_root_path': db_root_path,
            'db_mode': db_mode,
            'schema': schema,
            'language': language,
            **kwargs
        }

        # Verify that all required parameters are present and not None
        missing_params = [param for param in required_params if all_params.get(param) is None]
        if missing_params:
            raise ValueError(f"Missing required parameter{'s' if len(missing_params) > 1 else ''}: {', '.join(missing_params)}")

        with cls._lock:
            # Create a unique key based on initialization parameters
            instance_key = (host, port, dbname, user, password, db_root_path, db_mode,schema)
            
            # If the instance doesn't exist or parameters have changed, create a new instance
            if instance_key not in cls._instances:
                instance = cls(**all_params)
                cls._instances[instance_key] = instance
                
            return cls._instances[instance_key]

    def __init__(self, 
                host: str, 
                port: int, 
                dbname: str, 
                user: str, 
                password: str, 
                db_root_path: str='data',
                db_mode: str = "dev", 
                schema: str = "public",
                language: str = "English",
                **kwargs):
        """
        Initialize the PostgreSQL manager.
        
        Args:
            host (str): Database host.
            port (int): Database port.
            dbname (str): Database name.
            user (str): Database user.
            password (str): Database password.
            db_root_path (str): Path to the database root directory.
            db_mode (str, optional): Database mode (dev, prod, etc.). Defaults to "dev".
            schema (str, optional): Database schema. Defaults to "public".
            **kwargs: Additional parameters.
        """
        # Remove db_type from kwargs if it exists to avoid duplicate parameter
        kwargs_copy = kwargs.copy()
        if 'db_type' in kwargs_copy:
            del kwargs_copy['db_type']
        
        # Initialize the parent class
        super().__init__(db_root_path=db_root_path, db_mode=db_mode, db_type="postgresql", language=language, **kwargs_copy)
        
        # Only initialize once
        if not hasattr(self, '_initialized') or not self._initialized:
            self._validate_pg_params(host, port, dbname, user, password)
            
            # Set PostgreSQL specific attributes
            self.host = host
            self.port = port
            self.dbname = dbname
            self.user = user
            self.password = password
            self.schema = schema
            self.language = language
            
            # Set additional attributes from kwargs
            for key, value in kwargs.items():
                setattr(self, key, value)
            
            # Set up connection string and engine
            connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
            self.engine = create_engine(connection_string)
            
            # Set up directory path
            self._setup_directory_path(dbname)
            
            # Log initialization
            logging.debug(
                f"Initialized ThothPgManager with host={host}, port={port}, dbname={dbname}, "
                f"user={user}, schema={schema}"
            )
            
            self._initialized = True

    def _validate_pg_params(self, host: str, port: int, dbname: str, user: str, password: str) -> None:
        """
        Validate PostgreSQL specific parameters.
        
        Args:
            host (str): Database host.
            port (int): Database port.
            dbname (str): Database name.
            user (str): Database user.
            password (str): Database password.
            
        Raises:
            ValueError: If parameters are invalid.
            TypeError: If parameters have incorrect types.
        """
        # Type validation
        if not isinstance(port, int):
            raise TypeError("port must be an integer")
            
        # Value validation
        if not (1 <= port <= 65535):
            raise ValueError("port must be between 1 and 65535")
            
        # Required parameters validation
        if not host or not dbname or not user or password is None:
            raise ValueError("host, dbname, user, and password are required parameters")

    def __repr__(self):
        """
        String representation of the PostgreSQL manager.
        
        Returns:
            str: String representation.
        """
        return (
            f"ThothPgManager(host='{self.host}', port={self.port}, dbname='{self.dbname}', "
            f"user='{self.user}', schema='{self.schema}', db_mode='{self.db_mode}')"
        )

    def execute_sql(
            self,
            sql: str,
            params: Optional[Dict] = None,
            fetch: Union[str, int] = "all",
            timeout: int = 60,
    ) -> Any:
        """
        Execute SQL queries on PostgreSQL.

        Args:
            sql (str): The SQL query to execute.
            params (Optional[Dict], optional): Parameters for the SQL query. Defaults to None.
            fetch (Union[str, int], optional): Specifies how to fetch the results. Defaults to "all".
            timeout (int, optional): Timeout for the query execution. Defaults to 60.

        Returns:
            Any: The result of the SQL query execution.

        Raises:
            Exception: If there's an error executing the query.
        """
        with self.engine.connect() as connection:
            try:
                if params:
                    result = connection.execute(text(sql), params)
                else:
                    result = connection.execute(text(sql))

                if fetch == "all":
                    return [row._asdict() for row in result.fetchall()]
                elif fetch == "one":
                    row = result.fetchone()
                    return row._asdict() if row else None
                elif isinstance(fetch, int) and fetch > 0:
                    return [row._asdict() for row in result.fetchmany(fetch)]
                else:
                    connection.commit()
                    return result.rowcount
            except SQLAlchemyError as e:
                logging.error(f"Error executing SQL: {str(e)}")
                raise e

    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Retrieves unique text values from PostgreSQL database, excluding primary keys.
        The function is optimized to extract only meaningful values for LSH (Locality-Sensitive Hashing) analysis.

        Filtering Logic:
        1. Excludes primary keys to avoid non-meaningful identifier values
        2. Analyzes only text (str) type columns
        3. Excludes columns based on name patterns:
            - Suffixes: "Id"
            - Keywords: "_id", " id", "url", "email", "web", "time", "phone", "date", "address"
        
        Value Selection Criteria:
        A column is included if it meets any of these criteria:
        1. Contains "name" in its name AND has less than 5MB total data
        2. Has less than 2MB total data AND average length < 25 characters
        3. Has fewer than 100 distinct values

        Optimizations:
        - Pre-calculates statistics (sum length, count distinct) before extracting values
        - Uses distinct queries to avoid duplicates
        - Ignores NULL values
        
        Returns:
            Dict[str, Dict[str, List[str]]]: Hierarchical structure of unique values:
            {
                'table_name': {
                    'column_name': ['value1', 'value2', ...]
                }
            }

        Example:
            {
                'employees': {
                    'department': ['HR', 'IT', 'Sales'],
                    'position': ['Manager', 'Developer', 'Analyst']
                }
            }

        Notes:
            - Primarily used for building LSH indexes
            - Size thresholds (5MB, 2MB) are optimized to balance completeness and performance
            - Detailed logging helps with debugging and monitoring
        """
        inspector = inspect(self.engine)

        # Get all table names
        table_names = inspector.get_table_names(schema=self.schema)

        # Get primary keys
        primary_keys = []
        for table_name in table_names:
            pk_constraint = inspector.get_pk_constraint(table_name, schema=self.schema)
            primary_keys.extend(pk_constraint["constrained_columns"])

        unique_values: Dict[str, Dict[str, List[str]]] = {}

        with self.engine.connect() as connection:
            for table_name in table_names:
                logging.info(f"Processing {table_name}")

                # Get text columns that are not primary keys
                columns = [
                    col["name"]
                    for col in inspector.get_columns(table_name, schema=self.schema)
                    if col["type"].python_type == str
                       and col["name"] not in primary_keys
                ]

                table_values: Dict[str, List[str]] = {}

                for column in columns:
                    if any(
                            keyword in column.lower()
                            for keyword in [
                                "_id",
                                " id",
                                "url",
                                "email",
                                "web",
                                "time",
                                "phone",
                                "date",
                                "address",
                            ]
                    ) or column.endswith("Id"):
                        continue

                    try:
                        query = text(
                            f"""
                                SELECT SUM(LENGTH(unique_values)), COUNT(unique_values)
                                FROM (
                                    SELECT DISTINCT {column} AS unique_values
                                    FROM {self.schema}.{table_name}
                                    WHERE {column} IS NOT NULL
                                ) AS subquery
                            """
                        )
                        result = connection.execute(query).fetchone()
                    except SQLAlchemyError:
                        result = (0, 0)

                    sum_of_lengths, count_distinct = result
                    if sum_of_lengths is None or count_distinct == 0:
                        continue

                    average_length = sum_of_lengths / count_distinct
                    logging.info(
                        f"Column: {column}, sum_of_lengths: {sum_of_lengths}, count_distinct: {count_distinct}, average_length: {average_length}"
                    )

                    if (
                            ("name" in column.lower() and sum_of_lengths < 5000000)
                            or (sum_of_lengths < 2000000 and average_length < 25)
                            or count_distinct < 100
                    ):
                        logging.info(f"Fetching distinct values for {column}")
                        try:
                            query = text(
                                f"""
                                    SELECT DISTINCT {column}
                                    FROM {self.schema}.{table_name}
                                    WHERE {column} IS NOT NULL
                                """
                            )
                            values = [
                                str(value[0])
                                for value in connection.execute(query).fetchall()
                            ]
                        except SQLAlchemyError:
                            values = []
                        logging.info(f"Number of different values: {len(values)}")
                        table_values[column] = values

                unique_values[table_name] = table_values

        return unique_values

    def get_tables(self) -> List[Dict[str, str]]:
        """
        Get a list of tables in the PostgreSQL database with their comments.
        """
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names(schema=self.schema)
        tables_info = []
        with self.engine.connect() as connection:
            for table_name in table_names:
                comment = ''
                try:
                    # PostgreSQL specific way to get table comment
                    result = connection.execute(text(f"""
                        SELECT obj_description('{self.schema}.{table_name}'::regclass, 'pg_class');
                    """)).scalar()
                    if result:
                        comment = result
                except SQLAlchemyError as e:
                    logging.warning(f"Could not retrieve comment for table {table_name}: {e}")
                tables_info.append({'name': table_name, 'comment': comment})
        return tables_info

    def get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get a list of columns for a given table in the PostgreSQL database.
        Includes column name, data type, comment, and primary key status.
        """
        query = """
        SELECT
            c.column_name,
            c.data_type,
            c.ordinal_position,
            pgd.description,
            CASE
                WHEN kcu.column_name IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS is_pk
        FROM
            information_schema.columns c
        LEFT JOIN
            pg_catalog.pg_statio_all_tables as st
        ON
            c.table_schema = st.schemaname AND c.table_name = st.relname
        LEFT JOIN
            pg_catalog.pg_description pgd
        ON
            pgd.objoid = st.relid AND pgd.objsubid = c.ordinal_position
        LEFT JOIN
            information_schema.table_constraints tc
        ON
            tc.table_schema = c.table_schema AND tc.table_name = c.table_name AND tc.constraint_type = 'PRIMARY KEY'
        LEFT JOIN
            information_schema.key_column_usage kcu
        ON
            kcu.constraint_name = tc.constraint_name AND kcu.table_schema = tc.table_schema AND kcu.table_name = tc.table_name AND kcu.column_name = c.column_name
        WHERE
            c.table_schema = :schema AND c.table_name = :table_name
        ORDER BY
            c.ordinal_position;
        """
        with self.engine.connect() as connection:
            result = connection.execute(text(query), {"schema": self.schema, "table_name": table_name})
            columns_info = []
            for row in result:
                columns_info.append({
                    'name': row.column_name,
                    'data_type': row.data_type,
                    'comment': row.description,
                    'is_pk': row.is_pk,
                    'ordinal_position': row.ordinal_position
                })
            return columns_info

    def get_foreign_keys(self) -> List[Dict[str, str]]:
        """
        Get a list of foreign key relationships in the PostgreSQL database.
        """
        inspector = inspect(self.engine)
        all_foreign_keys = []
        for table_name in inspector.get_table_names(schema=self.schema):
            fks = inspector.get_foreign_keys(table_name, schema=self.schema)
            for fk in fks:
                all_foreign_keys.append({
                    'source_table_name': table_name,
                    'source_column_name': fk['constrained_columns'][0], # Assuming single column FK for simplicity
                    'target_table_name': fk['referred_table'],
                    'target_column_name': fk['referred_columns'][0] # Assuming single column FK for simplicity
                })
        return all_foreign_keys

    def get_table_schema(self, table_name: str) -> str:
        """
        Generates a markdown string describing the schema of the specified table.
        Uses SQLAlchemy inspector to get column metadata and tabulate to format.
        """
        inspector = inspect(self.engine)
        try:
            columns_metadata = inspector.get_columns(table_name, schema=self.schema)
        except SQLAlchemyError as e:
            logging.error(f"Error inspecting table {self.schema}.{table_name}: {e}")
            # Optionally, re-raise or return an error message
            raise e # Or return f"Error: Could not retrieve schema for table {table_name}."

        if not columns_metadata:
            return f"Table {self.schema}.{table_name} not found or has no columns."

        table_data_for_markdown = []
        for col_meta in columns_metadata:
            table_data_for_markdown.append({
                "column_name": col_meta['name'],
                "data_type": str(col_meta['type']),
                "nullable": col_meta['nullable'],
                "default": str(col_meta.get('default', 'N/A')), # Default might not always be present or string
                "comment": col_meta.get('comment', '') or '' # Ensure string, even if None
            })
        
        # Define headers for the markdown table
        # Note: 'comment' was part of the original plan based on get_training_plan_generic,
        # and 'nullable' & 'default' are common useful schema details.
        headers = {
            "column_name": "Column Name",
            "data_type": "Data Type",
            "nullable": "Nullable",
            "default": "Default",
            "comment": "Comment"
        }

        markdown_table = tabulate(table_data_for_markdown, headers=headers, tablefmt="pipe")
        
        db_name = self.dbname # Or self.engine.url.database
        intro_sentence = f"The following columns are in the {table_name} table in the {db_name} database (schema: {self.schema}):\n\n"
        
        final_doc = intro_sentence + markdown_table
        return final_doc

    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """
        Retrieves the most frequent values for each column in the specified table.
        Uses SQLAlchemy for database interaction.
        """
        inspector = inspect(self.engine)
        try:
            columns = inspector.get_columns(table_name, schema=self.schema)
        except SQLAlchemyError as e:
            logging.error(f"Error inspecting columns for table {self.schema}.{table_name}: {e}")
            raise e # Or return {}

        if not columns:
            logging.warning(f"No columns found for table {self.schema}.{table_name}")
            return {}

        most_frequent_values: Dict[str, List[Any]] = {}
        
        with self.engine.connect() as connection:
            for col_info in columns:
                column_name = col_info['name']
                # Ensure column name is properly quoted for the SQL query
                # The specific quoting character might depend on the SQL dialect,
                # but PostgreSQL uses double quotes.
                quoted_column_name = f'"{column_name}"'
                quoted_schema_name = f'"{self.schema}"'
                quoted_table_name = f'"{table_name}"'

                # Query to get most frequent values
                # Note: This query might be slow on very large tables without appropriate indexes.
                # It also assumes all column types can be meaningfully aggregated by COUNT.
                # For binary types or very large text fields, this might not be ideal.
                query_str = f"""
                    SELECT {quoted_column_name}
                    FROM (
                        SELECT {quoted_column_name}, COUNT(*) as _freq
                        FROM {quoted_schema_name}.{quoted_table_name}
                        WHERE {quoted_column_name} IS NOT NULL
                        GROUP BY {quoted_column_name}
                        ORDER BY _freq DESC
                        LIMIT :num_rows
                    ) as subquery;
                """
                try:
                    result = connection.execute(text(query_str), {"num_rows": number_of_rows})
                    values = [row[0] for row in result]
                    most_frequent_values[column_name] = values
                except SQLAlchemyError as e:
                    logging.error(f"Error fetching frequent values for {column_name} in {table_name}: {e}")
                    most_frequent_values[column_name] = [] # Or handle error differently

        # Normalize list lengths
        max_length = 0
        if most_frequent_values: # Check if dict is not empty
            max_length = max(len(v) for v in most_frequent_values.values()) if most_frequent_values else 0
        
        for column_name in most_frequent_values:
            current_len = len(most_frequent_values[column_name])
            if current_len < max_length:
                most_frequent_values[column_name].extend([None] * (max_length - current_len))
                
        return most_frequent_values
