import mysql.connector
import pandas as pd

class DatabaseConnection:
    def __init__(self, host, user, password, database):
        """
        Initializes the DatabaseConnection object with credentials and connects to the MySQL database.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.cursor = None
        self.connection = None
        self.__build_connection()
        self.__create_cursor()

    def __build_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        except mysql.connector.Error as err:
            self.__catch_exception(err)

    def __create_cursor(self):
        if self.connection:
            self.cursor = self.connection.cursor()
            print(f"\n✅ Connected to '{self.database}' successfully.\n")
        else:
            print("❌ Connection failed. Cursor not created.")

    def __catch_exception(self, error):
        print(f"❌ Database Error: {error}")

    def execute_read(self, query):
        """Executes a SELECT query and returns results as a pandas DataFrame."""
        try:
            self.cursor.execute(query)
            columns = [desc[0] for desc in self.cursor.description]
            data = self.cursor.fetchall()
            return pd.DataFrame(data=data, columns=columns)
        except mysql.connector.Error as err:
            self.__catch_exception(err)
            return None

    def execute_insert(self, query):
        """Executes an INSERT statement."""
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ Inserted successfully.")
        except mysql.connector.Error as err:
            self.__catch_exception(err)

    def execute_update(self, query):
        """Executes an UPDATE statement."""
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ Updated successfully.")
        except mysql.connector.Error as err:
            self.__catch_exception(err)

    def execute_delete(self, query):
        """Executes a DELETE statement."""
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("✅ Deleted successfully.")
        except mysql.connector.Error as err:
            self.__catch_exception(err)

    def execute_param_query(self, query, values):
        """Executes a parameterized query (safe against SQL injection)."""
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            print("✅ Executed parameterized query.")
        except mysql.connector.Error as err:
            self.__catch_exception(err)

    def close(self):
        """Closes the cursor and connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("✅ Connection closed.")

    def __del__(self):
        self.close()
