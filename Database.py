import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host="localhost", database="vetclinic", user="root", password="Panthers1!"):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def establish_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print("Successfully connected to the database")
                return self.connection
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return None

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")