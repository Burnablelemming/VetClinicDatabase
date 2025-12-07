"""Database connection helper.

Provides a thin wrapper around mysql.connector for connecting, cursor
access, commit and close operations.
"""

import mysql.connector
from mysql.connector import Error


class Database:
    def __init__(self, host="localhost", database="vetclinic", user="root", password="Panthers1!"):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    # Try to connect and return True/False
    def connect(self):
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

    # Return a buffered cursor or raise if not connected
    def get_cursor(self):
        if self.connection:
            return self.connection.cursor(buffered=True)
        raise ConnectionError("Database connection not established.")

    # Commit current transaction
    def commit(self):
        if self.connection:
            self.connection.commit()

    # Close connection if open
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
