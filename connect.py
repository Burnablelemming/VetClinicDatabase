import mysql.connector
from mysql.connector import Error
import Database

# ENVIRONMENT VARIABLES FOR DATABASE CONNECTION
def establish_connection():
    while True:
        host = input("Enter database host (default: localhost): ") or "localhost"
        database = input("Enter database name (default: vetclinic): ") or "vetclinic"
        user = input("Enter database user (default: root): ") or "root"
        password = input("Enter database password (default: Panthers1!): ") or "Panthers1!"
        
        db = Database.Database(host, database, user, password)

        if db.establish_connection():
            return db

def menu(cursor):
    # cursor used for executing queries
    # cursor.execute("SELECT * FROM your_table") as an example
    '''
    Considering pulling the table names directly from the database
    To keep the menu from being too cluttered:
    
    EXAMPLE MENU:
    1. View Tables (List all tables in the database)
    2. Query Data (Prompt for table name and conditions)
    3. Insert Data (Prompt for table name and data to insert)
    4. Update Data (Prompt for table name, conditions, and new data)
    5. Delete Data (Prompt for table name and conditions)
    6. Implements our custom functions from our DB model
    7. Exit
    '''

    pass



if __name__ == "__main__":
    db = establish_connection()
    menu(db.connection.cursor())


