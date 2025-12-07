# services.py
#
# The logic layer of the application.
# No SQL — only calls functions inside query.py.
# Does validation, printing, and commit handling.

import query

# ======================================================
#               GENERIC TABLE OPERATIONS
# ======================================================

def view_table(cursor, table_name):
    rows = query.select_all_from_table(cursor, table_name)
    return rows


def get_table_columns(cursor, table_name):
    return query.describe_table(cursor, table_name)


def insert_row(cursor, connection, table_name, columns, values):
    try:
        query.insert_into_table(cursor, table_name, columns, values)
        connection.commit()
        return True, "Insert successful."
    except Exception:
        return False, "Invalid input."



def update_row(cursor, connection, table_name, pk_column, pk_value, update_dict):
    try:
        query.update_table_row(cursor, table_name, pk_column, pk_value, update_dict)
        connection.commit()
        return True, "Update successful."
    except Exception:
        return False, "Invalid input."


def list_tables(cursor):
    return query.list_tables(cursor)



# ======================================================
#               OWNER / ANIMAL OPERATIONS
# ======================================================

def verify_owner_of_animal(cursor, owner_id, animal_id):
    """Returns tuple (is_valid, animal_name)."""
    result = query.get_animal_owner(cursor, animal_id)
    if not result:
        return False, None

    animal_owner, animal_name = result
    return (str(animal_owner) == str(owner_id)), animal_name


def list_pets_by_owner(cursor, owner_id):
    owner_exists = query.get_owner(cursor, owner_id)
    if not owner_exists:
        return None  # caller prints error

    return query.get_animals_by_owner(cursor, owner_id)


# ======================================================
#            APPOINTMENT & TREATMENT OPERATIONS
# ======================================================

def get_existing_treatments(cursor):
    return query.get_all_treatments(cursor)


def schedule_appointment_and_treatment(cursor, connection, owner_id, animal_id, vet_id, date_time, treatment_choice, new_treatment_type=None):
    try:
        # 1. Validate animal ownership
        is_owner, animal_name = verify_owner_of_animal(cursor, owner_id, animal_id)
        if not is_owner:
            return False, "Animal does not belong to owner."

        # 2. Validate veterinarian
        vet_result = query.get_vet_name(cursor, vet_id)
        if not vet_result:
            return False, "Veterinarian not found."
        vet_name = vet_result[0]

        # 3. Determine treatment type
        if treatment_choice == "0":
            treatment_type = new_treatment_type
        else:
            row = query.get_treatment_type_by_id(cursor, treatment_choice)
            if not row:
                return False, "Invalid Treatment ID."
            treatment_type = row[0]

        # 4. Insert appointment
        appt_id = query.insert_appointment(cursor, date_time, animal_id, vet_id)
        if not appt_id:
            appt_id = query.fallback_latest_appointment(cursor)

        # 5. Insert treatment
        query.insert_treatment(cursor, appt_id, treatment_type)

        connection.commit()

        return True, {
            "ApptID": appt_id,
            "DateTime": date_time,
            "Vet": vet_name,
            "Animal": animal_name,
            "Treatment": treatment_type
        }

    except Exception:
        return False, "Invalid input."

def get_appointment_summary(cursor, owner_id, animal_id):
    # Verify ownership
    #cursor.execute("SELECT Animal_OwnerID FROM Animal WHERE AnimalID = %s", (animal_id,))
    
    row = query.get_owner_of_animal(cursor, animal_id)

    if not row or str(row[0]) != str(owner_id):
        return False, "Animal does not belong to owner."

    # Fetch appointment/treatment summary
    rows = query.get_appointment_summary(cursor, animal_id)

    return True, rows


def cancel_appointment(cursor, connection, appt_id, animal_id):
    try:
        row = query.get_appt_animal(cursor, appt_id)
        if not row:
            return False, "Appointment not found."

        if str(row[0]) != str(animal_id):
            return False, "Appointment does not belong to this animal."

        query.delete_treatments_by_appt(cursor, appt_id)
        query.delete_appointment(cursor, appt_id)
        connection.commit()

        return True, f"Appointment {appt_id} and related treatments cancelled."

    except Exception:
        return False, "Invalid input."