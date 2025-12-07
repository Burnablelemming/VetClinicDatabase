import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host="localhost", database="vetclinic", user="root", password="Panthers1!"):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        """Establish a database connection."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return self.connection.is_connected()
        except Error as e:
            print(f"[DB ERROR] {e}")
            return False

    def get_cursor(self):
        """Return a buffered cursor."""
        if self.connection:
            return self.connection.cursor(buffered=True)
        raise ConnectionError("Database connection not established.")

    def commit(self):
        if self.connection:
            self.connection.commit()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
