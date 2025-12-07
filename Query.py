# query.py
#
# This module contains ONLY SQL queries.
# No printing, no input, no business logic, no commits.

def list_tables(cur):
    cur.execute("SHOW TABLES")
    return [t[0] for t in cur.fetchall()]


# ----------------------------
# Generic Table Operations
# ----------------------------

def describe_table(cur, table_name):
    cur.execute(f"DESCRIBE `{table_name}`")
    return cur.fetchall()


def select_all_from_table(cur, table_name, limit=1000):
    cur.execute(f"SELECT * FROM `{table_name}` LIMIT {limit}")
    return cur.fetchall()


def insert_into_table(cur, table_name, columns, values):
    """
    columns: list of column names
    values: list or tuple of values
    """
    placeholders = ", ".join(["%s"] * len(values))
    colnames = ", ".join([f"`{c}`" for c in columns])
    sql = f"INSERT INTO `{table_name}` ({colnames}) VALUES ({placeholders})"
    cur.execute(sql, tuple(values))


def update_table_row(cur, table_name, primary_key_col, pk_value, updates):
    """
    updates: dict of { column_name: new_value }
    """
    set_clause = ", ".join([f"`{col}` = %s" for col in updates.keys()])
    sql = f"UPDATE `{table_name}` SET {set_clause} WHERE `{primary_key_col}` = %s"
    params = list(updates.values()) + [pk_value]
    cur.execute(sql, params)


# ----------------------------
# Appointment & Treatment Queries
# ----------------------------

def get_all_treatments(cur):
    cur.execute("SELECT TreatmentID, TreatmentType FROM Treatment ORDER BY TreatmentID")
    return cur.fetchall()


def get_treatment_type_by_id(cur, treatment_id):
    cur.execute(
        "SELECT TreatmentType FROM Treatment WHERE TreatmentID = %s",
        (treatment_id,)
    )
    return cur.fetchone()


def insert_appointment(cur, date_time, animal_id, vet_id):
    sql = """
        INSERT INTO Appointment (DateTime, Scheduled_AnimalID, Treating_VetID)
        VALUES (%s, %s, %s)
    """
    cur.execute(sql, (date_time, animal_id, vet_id))
    return cur.lastrowid


def fallback_latest_appointment(cur):
    cur.execute("SELECT MAX(ApptID) FROM Appointment")
    row = cur.fetchone()
    return row[0] if row else None


def insert_treatment(cur, appointment_id, treatment_type):
    sql = """
        INSERT INTO Treatment (AppointmentID, TreatmentType)
        VALUES (%s, %s)
    """
    cur.execute(sql, (appointment_id, treatment_type))


def get_animal_owner(cur, animal_id):
    sql = "SELECT Animal_OwnerID, Aname FROM Animal WHERE AnimalID = %s"
    cur.execute(sql, (animal_id,))
    return cur.fetchone()


def get_vet_name(cur, vet_id):
    sql = "SELECT Vname FROM Veterinarian WHERE VetID = %s"
    cur.execute(sql, (vet_id,))
    return cur.fetchone()


def get_appointment_summary(cursor, animal_id):
    sql = """
        SELECT 
            a.ApptID,
            a.DateTime,
            t.TreatmentType,
            v.Vname
        FROM Appointment a
        JOIN Treatment t ON a.ApptID = t.AppointmentID
        LEFT JOIN Veterinarian v ON a.Treating_VetID = v.VetID
        WHERE a.Scheduled_AnimalID = %s
        ORDER BY a.DateTime DESC, a.ApptID
    """
    cursor.execute(sql, (animal_id,))
    return cursor.fetchall()


def delete_appointment(cur, appt_id):
    cur.execute("DELETE FROM Appointment WHERE ApptID = %s", (appt_id,))


def delete_treatments_by_appt(cur, appt_id):
    cur.execute("DELETE FROM Treatment WHERE AppointmentID = %s", (appt_id,))


# ----------------------------
# Owner / Animal Queries
# ----------------------------

def get_owner(cur, owner_id):
    cur.execute("SELECT * FROM Owner WHERE OwnerID = %s", (owner_id,))
    return cur.fetchone()


def get_animals_by_owner(cur, owner_id):
    sql = """
        SELECT AnimalID, Aname, Species, Breed, DOB
        FROM Animal
        WHERE Animal_OwnerID = %s
    """
    cur.execute(sql, (owner_id,))
    return cur.fetchall()


def get_appt_animal(cur, appt_id):
    cur.execute("SELECT Scheduled_AnimalID FROM Appointment WHERE ApptID = %s", (appt_id,))
    return cur.fetchone()


def get_owner_of_animal(cur, animal_id):
    """Return Animal_OwnerID for verification."""
    sql = "SELECT Animal_OwnerID FROM Animal WHERE AnimalID = %s"
    cur.execute(sql, (animal_id,))
    return cur.fetchone()
