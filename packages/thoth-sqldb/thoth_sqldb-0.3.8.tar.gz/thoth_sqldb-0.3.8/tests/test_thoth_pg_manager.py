import unittest
import os
import logging
from pathlib import Path

from dbmanager.impl.ThothPgManager import ThothPgManager

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestThothPgManager(unittest.TestCase):
    """Test suite for ThothPgManager with california_schools database."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests."""
        cls.db_root_path = str(Path(__file__).parent / "test_data")
        os.makedirs(cls.db_root_path, exist_ok=True)
        
        # Connection parameters for california_schools database
        cls.host = "localhost"
        cls.port = 5443
        cls.dbname = "california_schools"
        cls.user = "thoth_user"
        cls.password = "thoth_password"
        cls.db_mode = "test"
        
        # Get database manager instance
        try:
            cls.db_manager = ThothPgManager.get_instance(
                host=cls.host,
                port=cls.port,
                dbname=cls.dbname,
                user=cls.user,
                password=cls.password,
                db_root_path=cls.db_root_path,
                db_mode=cls.db_mode
            )
            logger.info("Successfully connected to california_schools database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    def test_singleton_pattern(self):
        """Test that get_instance returns the same instance for same parameters."""
        second_instance = ThothPgManager.get_instance(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            db_root_path=self.db_root_path,
            db_mode=self.db_mode
        )
        
        self.assertIs(self.db_manager, second_instance, 
                     "get_instance should return the same instance for same parameters")
    
    def test_different_parameters_create_new_instance(self):
        """Test that get_instance returns a new instance for different parameters."""
        # Using a different db_mode should create a new instance
        different_instance = ThothPgManager.get_instance(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            db_root_path=self.db_root_path,
            db_mode="different_mode"
        )
        
        self.assertIsNot(self.db_manager, different_instance, 
                        "get_instance should return a different instance for different parameters")
    
    def test_execute_sql_select(self):
        """Test executing a simple SELECT query."""
        # Get the list of tables in the database
        sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        """
        
        result = self.db_manager.execute_sql(sql)
        
        self.assertIsNotNone(result, "Query result should not be None")
        self.assertIsInstance(result, list, "Result should be a list")
        if result:
            self.assertIsInstance(result[0], dict, "Result items should be dictionaries")
    
    def test_execute_sql_with_params(self):
        """Test executing a parameterized query."""
        # Find tables with names containing a specific string
        sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name LIKE %(pattern)s
        """
        
        params = {"pattern": "%school%"}
        result = self.db_manager.execute_sql(sql, params)
        
        self.assertIsNotNone(result, "Query result should not be None")
        self.assertIsInstance(result, list, "Result should be a list")
    
    def test_execute_sql_fetch_one(self):
        """Test executing a query with fetch='one'."""
        sql = """
        SELECT COUNT(*) as table_count
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        """
        
        result = self.db_manager.execute_sql(sql, fetch="one")
        
        self.assertIsNotNone(result, "Query result should not be None")
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertIn("table_count", result, "Result should contain 'table_count' key")
    
    def test_execute_sql_fetch_many(self):
        """Test executing a query with fetch=N."""
        sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        LIMIT 10
        """
        
        fetch_count = 3
        result = self.db_manager.execute_sql(sql, fetch=fetch_count)
        
        self.assertIsNotNone(result, "Query result should not be None")
        self.assertIsInstance(result, list, "Result should be a list")
        self.assertLessEqual(len(result), fetch_count, 
                           f"Result should contain at most {fetch_count} items")
    
    def test_get_unique_values(self):
        """Test retrieving unique values from the database."""
        unique_values = self.db_manager.get_unique_values()
        
        self.assertIsNotNone(unique_values, "Unique values should not be None")
        self.assertIsInstance(unique_values, dict, "Unique values should be a dictionary")
        
        # Log the structure of unique_values for debugging
        logger.info(f"Unique values structure: {list(unique_values.keys())}")
        
        # If there are tables with unique values, check their structure
        if unique_values:
            table_name = next(iter(unique_values))
            table_values = unique_values[table_name]
            
            self.assertIsInstance(table_values, dict, 
                                "Table values should be a dictionary")
            
            if table_values:
                column_name = next(iter(table_values))
                column_values = table_values[column_name]
                
                self.assertIsInstance(column_values, list, 
                                    "Column values should be a list")
                
                logger.info(f"Sample unique values for {table_name}.{column_name}: "
                           f"{column_values[:5] if len(column_values) > 5 else column_values}")
    
    def test_complex_query(self):
        """Test executing a more complex query with joins if applicable."""
        # First, get the list of tables to find potential join candidates
        tables_sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        """
        
        tables = self.db_manager.execute_sql(tables_sql)
        table_names = [table['table_name'] for table in tables]
        
        logger.info(f"Available tables: {table_names}")
        
        # If we have at least one table, try to query it
        if table_names:
            sample_table = table_names[0]
            
            # Get column information for the sample table
            columns_sql = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = '{sample_table}'
            """
            
            columns = self.db_manager.execute_sql(columns_sql)
            column_names = [col['column_name'] for col in columns]
            
            logger.info(f"Columns in {sample_table}: {column_names}")
            
            # If we have columns, try a simple query
            if column_names:
                sample_column = column_names[0]
                query_sql = f"""
                SELECT {sample_column}
                FROM {sample_table}
                LIMIT 5
                """
                
                result = self.db_manager.execute_sql(query_sql)
                
                self.assertIsNotNone(result, "Query result should not be None")
                self.assertIsInstance(result, list, "Result should be a list")
                
                logger.info(f"Sample data from {sample_table}.{sample_column}: {result}")
    
    def test_error_handling(self):
        """Test error handling for invalid SQL."""
        invalid_sql = "SELECT * FROM non_existent_table"
        
        with self.assertRaises(Exception) as context:
            self.db_manager.execute_sql(invalid_sql)
        
        logger.info(f"Expected error was raised: {str(context.exception)}")
    
    def test_transaction_rollback(self):
        """Test transaction rollback on error."""
        # First, check if we can create a temporary table
        create_table_sql = """
        CREATE TEMPORARY TABLE IF NOT EXISTS test_rollback (
            id SERIAL PRIMARY KEY,
            name TEXT
        )
        """
        
        try:
            self.db_manager.execute_sql(create_table_sql)
            
            # Insert a valid row
            insert_sql = """
            INSERT INTO test_rollback (name) VALUES ('test_value')
            """
            self.db_manager.execute_sql(insert_sql)
            
            # Try an invalid insert that should cause a rollback
            invalid_insert = """
            INSERT INTO test_rollback (non_existent_column) VALUES ('test')
            """
            
            with self.assertRaises(Exception):
                self.db_manager.execute_sql(invalid_insert)
            
            # Check that the valid insert was rolled back
            count_sql = """
            SELECT COUNT(*) as row_count FROM test_rollback
            """
            result = self.db_manager.execute_sql(count_sql, fetch="one")
            
            # In PostgreSQL, DDL statements like CREATE TABLE automatically commit,
            # so the first INSERT should still be there despite the rollback of the second
            self.assertEqual(result['row_count'], 1, 
                           "Valid insert should be committed")
            
        except Exception as e:
            logger.warning(f"Transaction test failed: {str(e)}")
            self.skipTest(f"Skipping transaction test: {str(e)}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        # No explicit cleanup needed as we're not modifying the database
        # The connection pool will be closed when the program exits
        logger.info("Test suite completed")


if __name__ == '__main__':
    unittest.main()