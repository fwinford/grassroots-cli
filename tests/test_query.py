import os
import sqlite3
import sys
import unittest

# Ensure project root is in the module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.seed_db import seed_database, DB_PATH


class TestSeedDatabase(unittest.TestCase):
    """
    Unit tests for the seed_database function in db/seed_db.py
    """

    @classmethod
    def setUpClass(cls):
        # Remove existing database to test fresh seeding
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        seed_database()

    def test_db_file_created(self):
        """
        Test that the SQLite database file is created.
        """
        self.assertTrue(
            os.path.exists(DB_PATH),
            "Database file was not created."
        )

    def test_ntee_code_assigned(self):
        """
        Test that at least one org has a non-empty ntee_code field.
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM organizations WHERE ntee_code IS NOT NULL AND ntee_code != ''"
        )
        count = cursor.fetchone()[0]
        conn.close()
        self.assertGreater(
            count, 0,
            "No ntee_code values were assigned in the database."
        )


if __name__ == '__main__':
    unittest.main()
