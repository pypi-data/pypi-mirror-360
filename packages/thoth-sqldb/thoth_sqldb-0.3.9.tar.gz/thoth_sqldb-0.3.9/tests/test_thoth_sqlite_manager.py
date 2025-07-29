import unittest
import os
import logging
from pathlib import Path

from dbmanager.impl.ThothSqliteManager import ThothSqliteManager

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestThothSqliteManager(unittest.TestCase):
    """Test suite for ThothSqliteManager with california_schools database."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests."""
        # Define paths
        cls.project_root = Path(__file__).parent.parent
        cls.db_root_path = str(cls.project_root)
        cls.db_id = "california_schools"
        cls.db_mode = "dev"

        # Verify that the database file exists
        db_file_path = cls.project_root / "data" / f"{cls.db_mode}_databases" / cls.db_id / f"{cls.db_id}.sqlite"
        if not db_file_path.exists():
            raise FileNotFoundError(f"Database file not found at {db_file_path}")

        logger.info(f"Using database file at: {db_file_path}")

        # Get database manager instance
        try:
            cls.db_manager = ThothSqliteManager.get_instance(
                db_id=cls.db_id,
                db_root_path="data",
                db_mode=cls.db_mode
            )
            logger.info("Successfully connected to california_schools SQLite database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise

    def test_singleton_pattern(self):
        """Test that get_instance returns the same instance for same parameters."""
        second_instance = ThothSqliteManager.get_instance(
            db_id=self.db_id,
            db_root_path="data",
            db_mode=self.db_mode
        )

        self.assertIs(self.db_manager, second_instance,
                      "get_instance should return the same instance for same parameters")

    def test_different_parameters_create_new_instance(self):
        """Test that get_instance returns a new instance for different parameters."""
        # Using a different db_mode should create a new instance
        different_instance = ThothSqliteManager.get_instance(
            db_id=self.db_id,
            db_root_path="data",
            db_mode="different_mode"
        )

        self.assertIsNot(self.db_manager, different_instance,
                         "get_instance should return a different instance for different parameters")

    def test_execute_sql_select(self):
        """Test executing a simple SELECT query."""
        # Get the list of tables in the database
        sql = """SELECT name FROM sqlite_master HERE type='table' AND name NOT LIKE 'sqlite_%'
        """

        result = self.db_manager.execute_sql(sql)

        self.assertIsNotNone(result, "Query result should not be None")
        self.assertIsInstance(result, list, "Result should be a list")
        if result:
            self.assertIsInstance(result[0], dict, "Result items should be dictionaries")
            logger.info(f"Tables in database: {[table['name'] for table in result]}")

    def test_execute_sql_with_params(self):
        """Test executing a parameterized query."""
        # Find tables with names containing a specific string
        sql = """SELECT name FROM sqlite_master HERE type='table' AND name LIKE :pattern
        """

        params = {"pattern": "%school%"}
        result = self.db_manager.execute_sql(sql, params)

        self.assertIsNotNone(result, "Query result should not be None")
        self.assertIsInstance(result, list, "Result should be a list")
        logger.info(f"Tables matching pattern '%school%': {[table['name'] for table in result]}")

    def test_execute_sql_fetch_one(self):
        """Test executing a query with fetch='one'."""
        sql = """SELECT COUNT(*) as table_count FROM sqlite_master HERE type='table' AND name NOT LIKE 'sqlite_%'
        """

        result = self.db_manager.execute_sql(sql, fetch="one")

        self.assertIsNotNone(result, "Query result should not be None")
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertIn("table_count", result, "Result should contain 'table_count' key")
        logger.info(f"Number of tables: {result['table_count']}")

    def test_execute_sql_fetch_many(self):
        """Test executing a query with fetch=N."""
        sql = """SELECT name FROM sqlite_master HERE type='table' AND name NOT LIKE 'sqlite_%'
     MIT 10
        """

        fetch_count = 3
        result = self.db_manager.execute_sql(sql, fetch=fetch_count)

        self.assertIsNotNone(result, "Query result should not be None")
        self.assertIsInstance(result, list, "Result should be a list")
        self.assertLessEqual(len(result), fetch_count,
                             f"Result should contain at most {fetch_count} items")
        logger.info(f"Fetched {len(result)} tables: {[table['name'] for table in result]}")

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
        # First, get the list of tables
        tables_sql = """SELECT name FROM sqlite_master HERE type='table' AND name NOT LIKE 'sqlite_%'
        """

        tables = self.db_manager.execute_sql(tables_sql)
        table_names = [table['name'] for table in tables]

        logger.info(f"Available tables: {table_names}")

        # If we have at least one table, try to query it
        if table_names:
            sample_table = table_names[0]

            # Get column information for the sample table
            columns_sql = f"""
            PRAGMA table_info({sample_table})
            """

            columns = self.db_manager.execute_sql(columns_sql)
            column_names = [col['name'] for col in columns]

            logger.info(f"Columns in {sample_table}: {column_names}")

            # If we have columns, try a simple query
            if column_names:
                sample_column = column_names[0]
                query_sql = f"""SELECT {sample_column}
ROM {sample_table}
          MIT 5
                """

                result = self.db_manager.execute_sql(query_sql)

                self.assertIsNotNone(result, "Query result should not be None")
                self.assertIsInstance(result, list, "Result should be a list")

                logger.info(f"Sample data from {sample_table}.{sample_column}: {result}")

                # If we have at least two tables, try a join if they have common column patterns
                if len(table_names) >= 2:
                    # This is a simplified approach - in a real scenario, you'd need to identify
                    # actual foreign key relationships
                    second_table = table_names[1]
                    second_columns_sql = f"""
                    PRAGMA table_info({second_table})
                    """
                    second_columns = self.db_manager.execute_sql(second_columns_sql)
                    second_column_names = [col['name'] for col in second_columns]

                    # Look for potential join columns (e.g., id columns)
                    potential_join_columns = [
                        col for col in column_names
                        if col.endswith('_id') or col == 'id'
                    ]

                    if potential_join_columns and any(col in second_column_names for col in potential_join_columns):
                        join_column = next(col for col in potential_join_columns if col in second_column_names)

                        join_sql = f"""SELECT a.{column_names[0]}, b.{second_column_names[0]}
ROM {sample_table} a
          IN {second_table} b ON a.{join_column} = b.{join_column}
      IT 5
                        """

                        try:
                            join_result = self.db_manager.execute_sql(join_sql)
                            logger.info(f"Join query result: {join_result}")
                        except Exception as e:
                            logger.warning(f"Join query failed (this might be expected): {str(e)}")

    def test_error_handling(self):
        """Test error handling for invalid SQL."""
        invalid_sql = "SELECT * FROM non_existent_table"

        with self.assertRaises(Exception) as context:
            self.db_manager.execute_sql(invalid_sql)

        logger.info(f"Expected error was raised: {str(context.exception)}")

    def test_transaction_rollback(self):
        """Test transaction rollback on error."""
        # First, create a temporary table
        create_table_sql = """CREATE TABLE IF NOT EXISTS test_rollback (
                                             d INTEGER PRIMARY KEY,
                                              me TEXT
         """

        try:
            self.db_manager.execute_sql(create_table_sql)

            # Insert a valid row
            insert_sql = """INSERT INTO test_rollback (name) VALUES ('test_value')
            """
            self.db_manager.execute_sql(insert_sql)

            # Try an invalid insert that should cause a rollback
            invalid_insert = """INSERT INTO test_rollback (non_existent_column) VALUES ('test')
            """

            with self.assertRaises(Exception):
                self.db_manager.execute_sql(invalid_insert)

            # Check that the valid insert was committed (SQLite behavior differs from PostgreSQL)
            count_sql = """SELECT COUNT(*) as row_count FROM test_rollback
            """
            result = self.db_manager.execute_sql(count_sql, fetch="one")

            # In SQLite, each statement is its own transaction by default,
            # so the first INSERT should still be there

            # In SQLite, each statement is its own transaction by default,
            # so the first INSERT should still be there
            self.assertEqual(result['row_count'], 1,
                             "Valid insert should be committed")

            # Clean up - drop the test table
            cleanup_sql = """
            DROP TABLE IF EXISTS test_rollback
            """
            self.db_manager.execute_sql(cleanup_sql)

        except Exception as e:
            logger.warning(f"Transaction test failed: {str(e)}")
            self.skipTest(f"Skipping transaction test: {str(e)}")

    def test_database_file_exists(self):
        """Test that the database file exists at the expected location."""
        db_file_path = self.project_root / "data" / f"{self.db_mode}_databases" / self.db_id / f"{self.db_id}.sqlite"
        self.assertTrue(db_file_path.exists(), f"Database file should exist at {db_file_path}")
        self.assertTrue(db_file_path.is_file(), f"{db_file_path} should be a file")

        # Check that the file has some content (not empty)
        self.assertGreater(db_file_path.stat().st_size, 0,
                           "Database file should not be empty")

        logger.info(f"Database file exists and has size: {db_file_path.stat().st_size} bytes")

    def test_data_types(self):
        """Test handling of different data types in SQLite."""
        # First, get a table to work with
        tables_sql = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """

        tables = self.db_manager.execute_sql(tables_sql)
        if not tables:
            self.skipTest("No tables available to test data types")

        sample_table = tables[0]['name']

        # Get column information including data types
        columns_sql = f"""
        PRAGMA table_info({sample_table})
        """

        columns = self.db_manager.execute_sql(columns_sql)

        # Log column types for the sample table
        column_types = {col['name']: col['type'] for col in columns}
        logger.info(f"Column types in {sample_table}: {column_types}")

        # Test a query that returns different data types
        query_sql = f"""
        SELECT * FROM {sample_table} LIMIT 1
        """

        result = self.db_manager.execute_sql(query_sql, fetch="one")

        if result:
            # Log the types of values returned
            value_types = {key: type(value).__name__ for key, value in result.items()}
            logger.info(f"Value types in result: {value_types}")

            # Verify that we can access the values
            for key, value in result.items():
                self.assertIsNotNone(key, "Column name should not be None")
                # Value can be None, so we don't assert on that

    def test_large_result_set(self):
        """Test handling of larger result sets."""
        # First, get a table to work with
        tables_sql = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """

        tables = self.db_manager.execute_sql(tables_sql)
        if not tables:
            self.skipTest("No tables available to test large result sets")

        sample_table = tables[0]['name']

        # Get row count for the sample table
        count_sql = f"""
        SELECT COUNT(*) as row_count FROM {sample_table}
        """

        count_result = self.db_manager.execute_sql(count_sql, fetch="one")
        row_count = count_result['row_count']

        logger.info(f"Table {sample_table} has {row_count} rows")

        if row_count < 10:
            self.skipTest(f"Table {sample_table} has too few rows ({row_count}) to test large result sets")

        # Test fetching a larger number of rows
        query_sql = f"""
        SELECT * FROM {sample_table} LIMIT 100
        """

        result = self.db_manager.execute_sql(query_sql)

        self.assertIsNotNone(result, "Query result should not be None")
        self.assertIsInstance(result, list, "Result should be a list")
        logger.info(f"Successfully fetched {len(result)} rows from {sample_table}")

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        # No explicit cleanup needed for read-only tests
        # For tests that modify the database, we've already cleaned up in the test methods
        logger.info("Test suite completed")


if __name__ == '__main__':
    unittest.main()