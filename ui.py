# ui.py
#
# Handles user interaction: input prompts, printing, table selection.
# No SQL or business logic here.

import services

# ======================================================
#                   GENERIC UI HELPERS
# ======================================================

def prompt(message, default=None):
    """Generic input helper with default support."""
    value = input(f"{message} " + (f"(default: {default}): " if default else ": "))
    return value if value else default


def print_query_results(cursor, rows):
    """Print any SQL query result using column names from cursor.description."""

    if not rows:
        print("No results found.\n")
        return

    # Extract column names from the cursor
    col_names = [desc[0] for desc in cursor.description]

    # Calculate column widths (max of header or any row value)
    col_widths = []
    for i, name in enumerate(col_names):
        longest = len(name)
        for row in rows:
            value = row[i]

            # Format datetime → YYYY-MM-DD
            if hasattr(value, "strftime"):
                value = value.strftime("%Y-%m-%d")

            longest = max(longest, len(str(value)))
        col_widths.append(longest)

    # Print header row
    header = " | ".join(col_names[i].ljust(col_widths[i]) for i in range(len(col_names)))
    print("\n" + header)
    print("-" * len(header))

    # Print each row
    for row in rows:
        cells = []
        for i, value in enumerate(row):

            # Format datetime values
            if hasattr(value, "strftime"):
                value = value.strftime("%Y-%m-%d")

            cells.append(str(value).ljust(col_widths[i]))

        print(" | ".join(cells))

    print()


def print_dict_table(data_dict, title=None):
    """Prints a dictionary in a clean Field | Value table format."""
    
    if title:
        print(f"\n{title}")
        print("-" * len(title))

    # column widths
    max_key_len = max(len(str(k)) for k in data_dict.keys())
    header_key = "Field"
    header_val = "Value"

    # print header
    print(f"\n{header_key.ljust(max_key_len)} | {header_val}")
    print("-" * (max_key_len + 3 + len(header_val)))

    # print each row
    for key, value in data_dict.items():
        # format datetime
        if hasattr(value, "strftime"):
            value = value.strftime("%Y-%m-%d %H:%M:%S")

        print(f"{str(key).ljust(max_key_len)} | {value}")

# ======================================================
#                TABLE DISCOVERY & SELECTION
# ======================================================

def list_tables_ui(cursor):
    """Gets list of tables from DB and prints them."""
    tables = services.list_tables(cursor)
    if not tables:
        print("No tables found.")
        return []

    print("\nAvailable tables:")
    for i, t in enumerate(tables, start=1):
        print(f"{i}. {t}")
    return tables


def choose_table_ui(cursor):
    """Allows the user to pick ANY table from the database."""
    # cursor.execute("SHOW TABLES")
    # tables = [t[0] for t in cursor.fetchall()]

    tables = services.list_tables(cursor)

    if not tables:
        print("No tables available.")
        return None

    print("\nSelect a table:")
    for i, t in enumerate(tables, start=1):
        print(f"{i}. {t}")

    choice = input("Enter table number: ")

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(tables):
            return tables[idx]
    except:
        pass

    print("Invalid choice.")
    return None

def choose_insert_table_ui(cursor):
    """Allows the user to pick a table for INSERT, excluding restricted tables."""
    
    RESTRICTED_INSERT_TABLES = {"appointment", "treatment"}

    # cursor.execute("SHOW TABLES")
    # tables = [t[0] for t in cursor.fetchall()]

    tables = services.list_tables(cursor)

    # Filter out restricted tables
    valid_tables = [t for t in tables if t not in RESTRICTED_INSERT_TABLES]

    if not valid_tables:
        print("No valid tables available for insertion.")
        return None

    print("\nSelect a table to INSERT into:")
    for i, t in enumerate(valid_tables, start=1):
        print(f"{i}. {t}")

    choice = input("Enter table number: ")

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(valid_tables):
            return valid_tables[idx]
    except:
        pass

    print("Invalid choice.")
    return None


# ======================================================
#              SPECIALIZED APPOINTMENT UI
# ======================================================

def choose_treatment_ui(cursor):
    """Displays treatments and returns chosen ID or 0 for new one."""
    treatments = services.get_existing_treatments(cursor)
    
    print("\nExisting Treatments:")
    if not treatments:
        print("  None found.")
    else:
        for t_id, t_type in treatments:
            print(f"  {t_id} - {t_type}")

    print("\nEnter a TreatmentID from above.")
    print("Enter 0 to create a new treatment type.")

    choice = input("TreatmentID: ")
    return choice


def get_new_treatment_type_ui():
    """Prompt user for new treatment type."""
    return input("Enter NEW TreatmentType: ")


# ======================================================
#              INPUT PROMPTS FOR APPOINTMENTS
# ======================================================

def get_appointment_inputs():
    """Bundle all user prompts for appointment creation."""
    print("\nSchedule Appointment")

    owner_id = input("OwnerID: ")
    animal_id = input("AnimalID: ")
    vet_id = input("TreatingVetID: ")
    date_time = input("DateTime (YYYY-MM-DD): ")

    return owner_id, animal_id, vet_id, date_time


def get_treatment_summary_inputs():
    print("\nReturn Treatment Summary")
    owner_id = input("OwnerID: ")
    animal_id = input("AnimalID: ")
    return owner_id, animal_id


def get_cancel_appt_inputs():
    print("\nCancel Appointment")
    appt_id = input("Appointment ID: ")
    animal_id = input("AnimalID: ")
    return appt_id, animal_id


# ======================================================
#              PRINTING RESULTS FORMATTED
# ======================================================

def print_appointment_result(result_dict):
    print_dict_table(result_dict, title="Appointment Scheduled Successfully")


def print_pet_list(pets):
    if not pets:
        print("No pets registered for this owner.")
        return

    print("\nPets:")
    for pet in pets:
        animal_id, name, species, breed, dob = pet
        print(f"{animal_id} | {name} | {species} | {breed} | {dob}")


def print_treatment_summary(summary_rows):
    if not summary_rows:
        print("No treatments found.")
        return

    print("\nTreatment Summary:")
    for date, treatment, vet in summary_rows:
        print(f"{date} | {treatment} | {vet}")
