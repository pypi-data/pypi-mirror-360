import unittest
from mysql_wrapper import DatabaseConnection

class TestDBConnection(unittest.TestCase):
    def test_connection(self):
        try:
            db = DatabaseConnection('localhost', 'root', 'your_password', 'your_database')
            self.assertIsNotNone(db)
        except Exception as e:
            self.fail(f"Connection failed: {e}")

if __name__ == '__main__':
    unittest.main()
