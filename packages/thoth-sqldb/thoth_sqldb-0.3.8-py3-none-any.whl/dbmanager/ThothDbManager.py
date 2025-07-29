import pickle
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Union, ClassVar, Type, TypeVar
from dbmanager.helpers.search import _query_lsh

T = TypeVar('T', bound='ThothDbManager')

class ThothDbManager(ABC):
    """
    This class provides methods for interacting with a database.
    It follows a singleton pattern for each unique set of connection parameters.
    """
    _instances: ClassVar[Dict[tuple, Any]] = {}
    _lock: ClassVar[Lock] = Lock()

    @classmethod
    def get_instance(cls: Type[T], **kwargs) -> T:
        """
        Get or create a singleton instance based on connection parameters.
        
        Args:
            **kwargs: Connection parameters specific to the database implementation.
            
        Returns:
            An instance of the database manager.
            
        Raises:
            ValueError: If required parameters are missing.
        """
        # Implement in subclasses to handle specific parameters
        pass
    
    def __init__(self, db_root_path: str, db_mode: str = "dev", db_type: Optional[str] = None, **kwargs) -> None:
        """
        Initialize the database manager.
        
        Args:
            db_root_path (str): Path to the database root directory.
            db_mode (str, optional): Database mode (dev, prod, etc.). Defaults to "dev".
            db_type (Optional[str], optional): Type of database. Defaults to None.
            **kwargs: Additional parameters specific to the database implementation.
        """
        self._validate_common_params(db_root_path, db_mode)
        
        self.db_root_path = db_root_path
        self.db_mode = db_mode
        self.db_type = db_type
        
        # These will be set by subclasses
        self.engine = None
        self.db_id = None
        self.db_directory_path = None
        
        # LSH related attributes
        self.lsh = None
        self.minhashes = None
        self.vector_db = None
        
        # Flag to track initialization
        self._initialized = False
    
    def _validate_common_params(self, db_root_path: str, db_mode: str) -> None:
        """
        Validate common parameters for all database implementations.
        
        Args:
            db_root_path (str): Path to the database root directory.
            db_mode (str): Database mode (dev, prod, etc.).
            
        Raises:
            ValueError: If parameters are invalid.
        """
        if not db_root_path:
            raise ValueError("db_root_path is required")
        
        if not isinstance(db_mode, str):
            raise TypeError("db_mode must be a string")
    
    def _setup_directory_path(self, db_id: str) -> None:
        """
        Set up the database directory path.
        
        Args:
            db_id (str): Database identifier.
        """
        if isinstance(self.db_root_path, str):
            self.db_root_path = Path(self.db_root_path)
        
        self.db_directory_path = self.db_root_path / f"{self.db_mode}_databases" / db_id
        self.db_id = db_id

    @abstractmethod
    def execute_sql(self,
                   sql: str, 
                   params: Optional[Dict] = None, 
                   fetch: Union[str, int] = "all", 
                   timeout: int = 60) -> Any:
        """
        Abstract method to execute SQL queries.

        Args:
            sql (str): The SQL query to execute.
            params (Optional[Dict]): Parameters for the SQL query.
            fetch (Union[str, int]): Specifies how to fetch the results.
            timeout (int): Timeout for the query execution.

        Returns:
            Any: The result of the SQL query execution.
        """
        pass
    
    @abstractmethod
    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get unique values from the database.
        
        Returns:
            Dict[str, Dict[str, List[str]]]: Dictionary where:
                - outer key is table name
                - inner key is column name
                - value is list of unique values
        """
        pass

    @abstractmethod
    def get_tables(self) -> List[Dict[str, str]]:
        """
        Abstract method to get a list of tables in the database.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, where each dictionary
                                  represents a table with 'name' and 'comment' keys.
        """
        pass

    @abstractmethod
    def get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Abstract method to get a list of columns for a given table.

        Args:
            table_name (str): The name of the table.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                                  represents a column with 'name', 'data_type',
                                  'comment', and 'is_pk' keys.
        """
        pass

    @abstractmethod
    def get_foreign_keys(self) -> List[Dict[str, str]]:
        """
        Abstract method to get a list of foreign key relationships in the database.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, where each dictionary
                                  represents a foreign key relationship with
                                  'source_table_name', 'source_column_name',
                                  'target_table_name', and 'target_column_name' keys.
        """
        pass
    
    def set_lsh(self) -> str:
        """Sets the LSH and minhashes attributes by loading from pickle files."""
        with self._lock:
            if self.lsh is None:
                try:
                    lsh_path = self.db_directory_path / "preprocessed" / f"{self.db_id}_lsh.pkl"
                    minhashes_path = self.db_directory_path / "preprocessed" / f"{self.db_id}_minhashes.pkl"

                    if not lsh_path.exists() or not minhashes_path.exists():
                        raise FileNotFoundError(f"LSH or MinHashes file not found for {self.db_id}")

                    with lsh_path.open("rb") as file:
                        self.lsh = pickle.load(file)
                    with minhashes_path.open("rb") as file:
                        self.minhashes = pickle.load(file)
                    return "success"
                except Exception as e:
                    logging.error(f"Error loading LSH: {str(e)}")
                    self.lsh = "error"
                    self.minhashes = "error"
                    return "error"
            elif self.lsh == "error":
                return "error"
            else:
                return "success"

    def query_lsh(self,
                 keyword: str,
                 signature_size: int = 30,
                 n_gram: int = 3,
                 top_n: int = 10) -> Dict[str, Dict[str, List[str]]]:
        """
        Queries the LSH for similar values to the given keyword.

        Args:
            keyword (str): The keyword to search for.
            signature_size (int, optional): The size of the MinHash signature. Defaults to 30.
            n_gram (int, optional): The n-gram size for the MinHash. Defaults to 3.
            top_n (int, optional): The number of top results to return. Defaults to 10.

        Returns:
            Dict[str, Dict[str, List[str]]]: Dictionary where:
                - outer key is table name
                - inner key is column name
                - value is list of similar strings
        """
        lsh_status = self.set_lsh()
        if lsh_status == "success":
            return _query_lsh(self.lsh, self.minhashes, keyword, signature_size, n_gram, top_n)
        else:
            raise Exception(f"Error loading LSH for {self.db_id}")
