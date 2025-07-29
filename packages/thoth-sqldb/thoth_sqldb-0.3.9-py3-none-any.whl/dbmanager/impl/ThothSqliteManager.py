import logging
import os
from threading import Lock
from typing import Any, Dict, List, Optional, Union, Type, TypeVar

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from tabulate import tabulate

from ..ThothDbManager import ThothDbManager

T = TypeVar('T', bound='ThothSqliteManager')

class ThothSqliteManager(ThothDbManager):
    """
    SQLite implementation of ThothDbManager.
    """
    _instances = {}
    _lock = Lock()


    @classmethod
    def get_instance(cls: Type[T], 
                    db_id: str,
                    db_root_path: str,
                    db_mode: str = "dev",
                    language: str = "English",
                    **kwargs) -> T:
        required_params = ['db_id', 'db_root_path', 'language']

        all_params = {
            'db_id': db_id,
            'db_root_path': db_root_path,
            'db_mode': db_mode,
            'language': language,
            **kwargs
        }

        missing_params = [param for param in required_params if all_params.get(param) is None]
        if missing_params:
            raise ValueError(f"Missing required parameter{'s' if len(missing_params) > 1 else ''}: {', '.join(missing_params)}")

        with cls._lock:
            instance_key = (db_id, db_root_path, db_mode)
            
            if instance_key not in cls._instances:
                instance = cls(**all_params)
                cls._instances[instance_key] = instance
                
            return cls._instances[instance_key]

    def __init__(self, 
                db_id: str,
                db_root_path: str,
                db_mode: str = "dev",
                language: str = "English",
                **kwargs):
        kwargs_copy = kwargs.copy()
        if 'db_type' in kwargs_copy:
            del kwargs_copy['db_type']
        
        super().__init__(db_root_path=db_root_path, db_mode=db_mode, db_type="sqlite", language=language, **kwargs_copy)
        
        if not hasattr(self, '_initialized') or not self._initialized:
            self._validate_sqlite_params(db_id, db_root_path)
            
            self.db_id = db_id
            
            self._setup_directory_path(db_id)
            
            os.makedirs(self.db_directory_path, exist_ok=True)
            
            db_file_path = self.db_directory_path / f"{self.db_id}.sqlite"
            connection_string = f"sqlite:///{db_file_path}"
            self.engine = create_engine(connection_string)
            
            for key, value in kwargs.items():
                setattr(self, key, value)
            
            logging.debug(
                f"Initialized ThothSqliteManager with db_id={db_id}, "
                f"db_path={db_file_path}, db_mode={db_mode}"
            )
            
            self._initialized = True

    def _validate_sqlite_params(self, db_id: str, db_root_path: str) -> None:
        if not isinstance(db_id, str):
            raise TypeError("db_id must be a string")
            
        if not isinstance(db_root_path, str):
            raise TypeError("db_root_path must be a string")
            
        if not db_id:
            raise ValueError("db_id cannot be empty")

    @property
    def schema(self) -> str:
        """
        SQLite schema property. SQLite uses 'main' as the default schema name.
        """
        return ""

    def __repr__(self):
        return (
            f"ThothSqliteManager(db_id='{self.db_id}', "
            f"db_path='{self.db_directory_path / f'{self.db_id}.sqlite'}', "
            f"db_mode='{self.db_mode}')"
        )

    def execute_sql(
            self,
            sql: str,
            params: Optional[Dict] = None,
            fetch: Union[str, int] = "all",
            timeout: int = 60,
    ) -> Any:
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

    def get_tables(self) -> List[Dict[str, str]]:
        """
        Get a list of tables in the SQLite database.
        SQLite does not have table comments, so an empty string is returned for comments.
        """
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()
        tables_info = []
        for table_name in table_names:
            tables_info.append({'name': table_name, 'comment': ''})
        return tables_info

    def get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get a list of columns for a given table in the SQLite database.
        Includes column name, data type, and primary key status.
        SQLite does not have column comments, so an empty string is returned for comments.
        """
        inspector = inspect(self.engine)
        columns_metadata = inspector.get_columns(table_name)
        pk_columns = inspector.get_pk_constraint(table_name).get('constrained_columns', [])

        columns_info = []
        for col_meta in columns_metadata:
            columns_info.append({
                'name': col_meta['name'],
                'data_type': str(col_meta['type']),
                'comment': '',  # SQLite does not have column comments
                'is_pk': col_meta['name'] in pk_columns
            })
        return columns_info

    def get_foreign_keys(self) -> List[Dict[str, str]]:
        """
        Get a list of foreign key relationships in the SQLite database.
        """
        inspector = inspect(self.engine)
        all_foreign_keys = []
        for table_name in inspector.get_table_names():
            fks = inspector.get_foreign_keys(table_name)
            for fk in fks:
                all_foreign_keys.append({
                    'source_table_name': table_name,
                    'source_column_name': fk['constrained_columns'][0],
                    'target_table_name': fk['referred_table'],
                    'target_column_name': fk['referred_columns'][0]
                })
        return all_foreign_keys

    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Retrieves unique text values from SQLite database.
        The function is optimized to extract only meaningful values for LSH (Locality-Sensitive Hashing) analysis.

        Filtering Logic:
        1. Analyzes only text type columns
        2. Excludes columns based on name patterns:
            - Suffixes: "Id"
            - Keywords: "_id", " id", "url", "email", "web", "time", "phone", "date", "address"
        
        Value Selection Criteria:
        A column is included if it meets any of these criteria:
        1. Contains "name" in its name
        2. Has average length < 25 characters
        3. Has fewer than 100 distinct values

        Returns:
            Dict[str, Dict[str, List[str]]]: Hierarchical structure of unique values:
            {
                'table_name': {
                    'column_name': ['value1', 'value2', ...]
                }
            }
        """
        inspector = inspect(self.engine)
        
        table_names = inspector.get_table_names()
        
        unique_values: Dict[str, Dict[str, List[str]]] = {}
        
        with self.engine.connect() as connection:
            for table_name in table_names:
                logging.info(f"Processing {table_name}")
                
                columns_info = inspector.get_columns(table_name)
                
                text_columns = []
                for col in columns_info:
                    col_type = str(col['type']).lower()
                    if 'char' in col_type or 'text' in col_type or 'varchar' in col_type:
                        text_columns.append(col['name'])
                
                table_values: Dict[str, List[str]] = {}
                
                for column in text_columns:
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
                            SELECT 
                                COUNT(DISTINCT "{column}") as count_distinct,
                                AVG(LENGTH("{column}")) as avg_length
                            FROM "{table_name}"
                            WHERE "{column}" IS NOT NULL
                            """
                        )
                        stats_result = connection.execute(query).fetchone()
                        
                        count_distinct = stats_result[0] if stats_result else 0
                        avg_length = stats_result[1] if stats_result and stats_result[1] is not None else 0.0
                        
                        if count_distinct == 0:
                            continue
                            
                        logging.info(
                            f"Column: {column}, count_distinct: {count_distinct}, average_length: {avg_length}"
                        )
                        
                        if (
                                "name" in column.lower()
                                or (avg_length is not None and avg_length < 25) # Ensure avg_length is not None
                                or count_distinct < 100
                        ):
                            logging.info(f"Fetching distinct values for {column}")
                            query_distinct_values = text(
                                f"""
                                SELECT DISTINCT "{column}"
                                FROM "{table_name}"
                                WHERE "{column}" IS NOT NULL
                                """
                            )
                            values = [
                                str(value_row[0])
                                for value_row in connection.execute(query_distinct_values).fetchall()
                            ]
                            logging.info(f"Number of different values: {len(values)}")
                            table_values[column] = values
                    except SQLAlchemyError as e:
                        logging.error(f"Error processing column {column} in table {table_name} ({self.db_id}.sqlite): {str(e)}")
                        continue 
                
                if table_values:
                    unique_values[table_name] = table_values
        
        return unique_values

    def get_table_schema(self, table_name: str) -> str:
        """
        Generates a markdown string describing the schema of the specified table.
        Uses SQLAlchemy inspector to get column metadata and tabulate to format.
        """
        inspector = inspect(self.engine)
        try:
            columns_metadata = inspector.get_columns(table_name) 
        except SQLAlchemyError as e:
            logging.error(f"Error inspecting table {table_name} in {self.db_id}.sqlite: {e}")
            raise e 

        if not columns_metadata:
            return f"Table {table_name} not found or has no columns in {self.db_id}.sqlite."

        table_data_for_markdown = []
        for col_meta in columns_metadata:
            table_data_for_markdown.append({
                "column_name": col_meta['name'],
                "data_type": str(col_meta['type']),
                "nullable": col_meta['nullable'],
                "default": str(col_meta.get('default', 'N/A')),
                "comment": col_meta.get('comment', '') or '' 
            })
        
        headers = {
            "column_name": "Column Name",
            "data_type": "Data Type",
            "nullable": "Nullable",
            "default": "Default",
            "comment": "Comment"
        }

        markdown_table = tabulate(table_data_for_markdown, headers=headers, tablefmt="pipe")
        
        intro_sentence = f"The following columns are in the {table_name} table in the {self.db_id}.sqlite database:\n\n"
        
        final_doc = intro_sentence + markdown_table
        return final_doc

    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """
        Retrieves the most frequent values for each column in the specified table.
        Uses SQLAlchemy for database interaction.
        """
        inspector = inspect(self.engine)
        try:
            columns = inspector.get_columns(table_name) 
        except SQLAlchemyError as e:
            logging.error(f"Error inspecting columns for table {table_name} in {self.db_id}.sqlite: {e}")
            raise e

        if not columns:
            logging.warning(f"No columns found for table {table_name} in {self.db_id}.sqlite")
            return {}

        most_frequent_values: Dict[str, List[Any]] = {}
        
        with self.engine.connect() as connection:
            for col_info in columns:
                column_name = col_info['name']
                quoted_column_name = f'"{column_name}"'
                quoted_table_name = f'"{table_name}"'

                query_str = f"""
                    SELECT {quoted_column_name}
                    FROM (
                        SELECT {quoted_column_name}, COUNT(*) as _freq
                        FROM {quoted_table_name} 
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
                    logging.error(f"Error fetching frequent values for {column_name} in {table_name} ({self.db_id}.sqlite): {e}")
                    most_frequent_values[column_name] = [] 

        max_length = 0
        if most_frequent_values:
            max_length = max(len(v) for v in most_frequent_values.values()) if most_frequent_values else 0
        
        for column_name_key in most_frequent_values:
            current_len = len(most_frequent_values[column_name_key])
            if current_len < max_length:
                most_frequent_values[column_name_key].extend([None] * (max_length - current_len))
                
        return most_frequent_values
