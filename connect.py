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

def list_tables(cur):
    cur.execute("SHOW TABLES")
    tables = [t[0] for t in cur.fetchall()]
    return tables


def choose_table(cur):
    tables = list_tables(cur)
    if not tables:
        print("No tables found in the database.")
        return None
    print("Select a table:")
    for i, t in enumerate(tables, start=1):
        print(f"{i}. {t}")
    choice = input("Enter table number: ")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(tables):
            return tables[idx]
    except ValueError:
        pass
    print("Invalid selection.")
    return None


def view_table(cur):
    table = choose_table(cur)
    if not table:
        return
    cur.execute(f"SELECT * FROM `{table}` LIMIT 1000")
    rows = cur.fetchall()
    if not rows:
        print(f"No rows in table {table}.")
        return
    for row in rows:
        print(row)


def insert_into_table(cur, conn):
    table = choose_table(cur)
    if not table:
        return
    cur.execute(f"DESCRIBE `{table}`")
    cols = cur.fetchall()
    insert_cols = []
    values = []
    for col in cols:
        name = col[0]
        extra = col[5]
        if "auto_increment" in (extra or ""):
            continue
        if name == 'DOB':
            val = input(f"Enter value for {name} expected (YYYY-MM-DD): ")
        elif name == 'AnimalID':
            val = input(f"Enter value for {name} expected (Integer): ")
        elif name == 'Species':
            val = input(f"Enter value for {name} (e.g. Dog, Cat): ")
        elif name == 'Animal_OwnerID':
            val = input(f"Enter value for {name} expected (Integer OwnerID): ")
        else:
            val = input(f"Enter value for {name} (leave blank for NULL): ")
        if val == "":
            values.append(None)
        else:
            values.append(val)
        insert_cols.append(name)
    if not insert_cols:
        print("No writable columns found.")
        return
    placeholders = ",".join(["%s"] * len(insert_cols))
    colnames = ",".join([f"`{c}`" for c in insert_cols])
    sql = f"INSERT INTO `{table}` ({colnames}) VALUES ({placeholders})"
    cur.execute(sql, tuple(values))
    conn.commit()
    print("Insert successful.")


def update_entry(cur, conn):
    table = choose_table(cur)
    if not table:
        return
    cur.execute(f"DESCRIBE `{table}`")
    cols = cur.fetchall()
    pk = None
    for col in cols:
        if col[3] == 'PRI':
            pk = col[0]
            break
    if not pk:
        pk = input("No primary key detected. Enter the column name to use as key: ")
    key_val = input(f"Enter {pk} value to identify the row to update: ")
    print("Columns:")
    updatable = [c[0] for c in cols if c[0] != pk]
    for i, c in enumerate(updatable, start=1):
        print(f"{i}. {c}")
    choices = input("Enter comma-separated column numbers to update (e.g. 1,3): ")
    try:
        idxs = [int(x.strip()) - 1 for x in choices.split(",") if x.strip()]
    except ValueError:
        print("Invalid selection.")
        return
    updates = []
    params = []
    for i in idxs:
        if 0 <= i < len(updatable):
            col = updatable[i]
            val = input(f"Enter new value for {col} (leave blank for NULL): ")
            updates.append(f"`{col}` = %s")
            params.append(None if val == "" else val)
    if not updates:
        print("No updates specified.")
        return
    params.append(key_val)
    sql = f"UPDATE `{table}` SET {', '.join(updates)} WHERE `{pk}` = %s"
    cur.execute(sql, tuple(params))
    conn.commit()
    print("Update committed.")


def schedule_appointment_and_treatment(cur, conn):
    print("Schedule Appointment and Treatment")
    owner_id = input("OwnerID: ")
    animal_id = input("AnimalID: ")
    vet_id = input("TreatingVetID: ")
    appt_dt = input("DateTime (YYYY-MM-DD HH:MM:SS): ")
    print("\nExisting Treatment Types:")
    cur.execute("SELECT TreatmentID, TreatmentType FROM Treatment ORDER BY TreatmentID")
    existing = cur.fetchall()

    if existing:
        for t in existing:
            print(f"  {t[0]} - {t[1]}")
    else:
        print("  No treatments exist yet.")

    print("\nEnter a TreatmentID from above.")
    print("Enter 0 to add a NEW treatment type.")

    treatment_choice = input("TreatmentID: ")

    if treatment_choice == "0":
        # user wants a new treatment type
        treatment_type = input("Enter NEW TreatmentType: ")
    else:
        # use an existing treatment type
        cur.execute("SELECT TreatmentType FROM Treatment WHERE TreatmentID = %s", (treatment_choice,))
        row = cur.fetchone()
        if not row:
            print("Invalid TreatmentID.")
            return
        treatment_type = row[0]

    # Verify Animal belongs to Owner
    cur.execute("SELECT Animal_OwnerID, Aname FROM Animal WHERE AnimalID = %s", (animal_id,))
    arow = cur.fetchone()
    if not arow:
        print("Animal not found.")
        return
    animal_owner = arow[0]
    animal_name = arow[1] if len(arow) > 1 else None
    if str(animal_owner) != str(owner_id):
        print("The provided AnimalID does not belong to the provided OwnerID.")
        return

    # Verify Vet exists
    cur.execute("SELECT Vname FROM Veterinarian WHERE VetID = %s", (vet_id,))
    vrow = cur.fetchone()
    if not vrow:
        print("Veterinarian not found.")
        return
    vet_name = vrow[0]

    # Insert Appointment
    cur.execute("INSERT INTO Appointment (DateTime, Scheduled_AnimalID, Treating_VetID) VALUES (%s, %s, %s)", (appt_dt, animal_id, vet_id))
    conn.commit()
    appt_id = cur.lastrowid
    if not appt_id:
        # fallback
        cur.execute("SELECT MAX(ApptID) FROM Appointment")
        appt_id = cur.fetchone()[0]

    # Insert Treatment
    cur.execute("INSERT INTO Treatment (AppointmentID, TreatmentType) VALUES (%s, %s)", (appt_id, treatment_type))
    conn.commit()

    print("Appointment and treatment scheduled:")
    print(f"ApptID: {appt_id}, DateTime: {appt_dt}, Vet: {vet_name}, Animal: {animal_name}, Treatment: {treatment_type}")


def return_treatment_summary(cur, conn):
    print("Return Treatment Summary")
    owner_id = input("OwnerID: ")
    animal_id = input("AnimalID: ")

    # Verify ownership
    cur.execute("SELECT Animal_OwnerID FROM Animal WHERE AnimalID = %s", (animal_id,))
    row = cur.fetchone()
    if not row or str(row[0]) != str(owner_id):
        print("Animal does not belong to the owner or not found.")
        return

    sql = ("SELECT a.DateTime, t.TreatmentType, v.Vname "
           "FROM Appointment a "
           "JOIN Treatment t ON a.ApptID = t.AppointmentID "
           "LEFT JOIN Veterinarian v ON a.Treating_VetID = v.VetID "
           "WHERE a.Scheduled_AnimalID = %s "
           "ORDER BY a.DateTime DESC")
    cur.execute(sql, (animal_id,))
    rows = cur.fetchall()
    if not rows:
        print("No treatments found for this animal.")
        return
    for r in rows:
        print(f"Date: {r[0]}, Treatment: {r[1]}, Veterinarian: {r[2]}")


def cancel_appointment(cur, conn):
    print("Cancel Appointment")
    appt_id = input("ApptID: ")
    animal_id = input("AnimalID: ")

    cur.execute("SELECT Scheduled_AnimalID FROM Appointment WHERE ApptID = %s", (appt_id,))
    row = cur.fetchone()
    if not row:
        print("Appointment not found.")
        return
    if str(row[0]) != str(animal_id):
        print("Appointment does not belong to the provided AnimalID.")
        return

    cur.execute("DELETE FROM Treatment WHERE AppointmentID = %s", (appt_id,))
    cur.execute("DELETE FROM Appointment WHERE ApptID = %s", (appt_id,))
    conn.commit()
    print(f"Appointment {appt_id} and related treatments cancelled.")


def list_pets_by_owner(cur, conn):
    print("List Pets By Owner")
    owner_id = input("OwnerID: ")
    cur.execute("SELECT * FROM Owner WHERE OwnerID = %s", (owner_id,))
    if not cur.fetchone():
        print("Owner not found.")
        return
    cur.execute("SELECT AnimalID, Aname, Species, Breed, DOB FROM Animal WHERE Animal_OwnerID = %s", (owner_id,))
    rows = cur.fetchall()
    if not rows:
        print("No registered animals for this owner.")
        return
    for r in rows:
        print(f"AnimalID: {r[0]}, Name: {r[1]}, Species: {r[2]}, Breed: {r[3]}, DOB: {r[4]}")


def menu(cursor, connection):
    while True:
        print("\nMenu:")
        print("1. View all tables (select table to view)")
        print("2. Insert into table")
        print("3. Update entry in table")
        print("4. Schedule Appointment and Treatment")
        print("5. Return Treatment Summary")
        print("6. Cancel Appointment")
        print("7. List Pets By Owner")
        print("8. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            view_table(cursor)
        elif choice == '2':
            insert_into_table(cursor, connection)
        elif choice == '3':
            update_entry(cursor, connection)
        elif choice == '4':
            schedule_appointment_and_treatment(cursor, connection)
        elif choice == '5':
            return_treatment_summary(cursor, connection)
        elif choice == '6':
            cancel_appointment(cursor, connection)
        elif choice == '7':
            list_pets_by_owner(cursor, connection)
        elif choice == '8':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")




if __name__ == "__main__":
    db = establish_connection()
    menu(db.connection.cursor(), db.connection)
    db.close_connection()


