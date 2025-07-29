import unittest
from dbmanager.helpers.search import _query_lsh, load_db_lsh

class TestLSHQuery(unittest.TestCase):
    def test_query_lsh_interactive(self):
        """
        Interactive test to query the LSH with a keyword and print the results.
        """
        # --- USER INPUT ---
        db_directory_path = (
            input("Enter the path to the database directory [/Users/mp/DjangoExperimental/Thoth/data/dev_databases/california_schools]: ")
            or "/Users/mp/DjangoExperimental/Thoth/data/dev_databases/california_schools"
        )
        keyword = input("Enter the keyword to search for [meals]: ") or "meals"
        signature_size = int(
            input("Enter the signature size (e.g., 30) [30]: ") or 30
        )
        n_gram = int(input("Enter the n-gram size (e.g., 9) [9]: ") or 9)
        top_n = int(input("Enter the number of results to return (e.g., 5) [5]: ") or 5)
        # ------------------

        try:
            lsh, minhashes = load_db_lsh(db_directory_path)
        except FileNotFoundError:
            self.fail(
                f"LSH data not found in '{db_directory_path}'. "
                "Please ensure the path is correct and the data exists."
            )

        print(f"\n--- Running LSH Query Test ---")
        print(f"Database Path: '{db_directory_path}'")
        print(f"Keyword: '{keyword}'")
        print(f"Signature Size: {signature_size}")
        print(f"N-gram: {n_gram}")
        print(f"Top N: {top_n}")
        print("--------------------------------\n")

        # Query the LSH
        results = _query_lsh(
            lsh,
            minhashes,
            keyword,
            signature_size=signature_size,
            n_gram=n_gram,
            top_n=top_n,
        )

        # Print the results
        print("--- Query Results ---")
        if not results:
            print("No results found.")
        else:
            for table, columns in results.items():
                print(f"Table: {table}")
                for col, values in columns.items():
                    print(f"  Column: {col}")
                    for val in values:
                        print(f"    - {val}")
        print("---------------------\n")

        # This is an interactive test, so we don't assert anything specific.
        # The goal is to observe the output.
        self.assertIsNotNone(results, "The result should not be None")

if __name__ == "__main__":
    unittest.main()
