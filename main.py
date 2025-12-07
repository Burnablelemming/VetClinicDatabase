# main.py
#
# Clean controller / entry point.
# No SQL. No business logic.
# Just the menu and calls into ui + services.

from Database import Database
import ui
import services


def establish_connection_ui():
    """Repeatedly prompts user for DB info until connection is successful."""
    while True:
        print("\nEnter database login details:")
        host = ui.prompt("Host", "localhost")
        dbname = ui.prompt("Database name", "vetclinic")
        user = ui.prompt("User", "root")
        password = ui.prompt("Password", "Panthers1!")

        db = Database(host, dbname, user, password)

        if db.connect():
            print("Connected to database successfully.\n")
            return db
        else:
            print("Connection failed. Try again.\n")


def main():
    db = establish_connection_ui()
    cursor = db.get_cursor()

    while True:
        print("\n=== Vet Clinic Menu ===")
        print("1. View Table")
        print("2. Insert Into Table")
        print("3. Update Table Entry")
        print("4. Schedule Appointment + Treatment")
        print("5. Treatment Summary")
        print("6. Cancel Appointment")
        print("7. List Pets By Owner")
        print("8. Exit")

        choice = input("Enter choice: ")

        # ------------------------------------------------------
        # 1. VIEW TABLE
        # ------------------------------------------------------
        if choice == "1":
            table = ui.choose_table_ui(cursor)
            if table:
                rows = services.view_table(cursor, table)
                ui.print_query_results(cursor, rows)

        # ------------------------------------------------------
        # 2. INSERT INTO TABLE
        # ------------------------------------------------------
        elif choice == "2":
            table = ui.choose_insert_table_ui(cursor)
            if not table:
                continue

            cols = services.get_table_columns(cursor, table)

            insert_cols = []
            values = []

            print("\nEnter values (blank → NULL):\n")

            for col in cols:
                name = col[0]
                extra = col[5]

                # skip auto-increment
                if "auto_increment" in (extra or ""):
                    continue

                val = input(f"{name}: ")
                insert_cols.append(name)
                values.append(val if val != "" else None)

            success, msg = services.insert_row(cursor, db.connection, table, insert_cols, values)
            print(msg)


        # ------------------------------------------------------
        # 3. UPDATE ENTRY
        # ------------------------------------------------------
        elif choice == "3":
            table = ui.choose_table_ui(cursor)
            if not table:
                continue

            cols = services.get_table_columns(cursor, table)

            pk_col = None
            for col in cols:
                if col[3] == "PRI":
                    pk_col = col[0]
                    break

            if not pk_col:
                pk_col = input("Enter primary key column: ")

            pk_value = input(f"{pk_col} value: ")

            print("\nColumns:")
            non_pk_cols = [c[0] for c in cols if c[0] != pk_col]

            for i, c in enumerate(non_pk_cols, start=1):
                print(f"{i}. {c}")

            choices = input("Enter columns to update (comma-separated): ")

            updates = {}
            for num in choices.split(","):
                try:
                    idx = int(num.strip()) - 1
                    if 0 <= idx < len(non_pk_cols):
                        col = non_pk_cols[idx]
                        new_val = input(f"New value for {col} (blank → NULL): ")
                        updates[col] = new_val if new_val != "" else None
                except:
                    pass

            success, msg = services.update_row(cursor, db.connection, table, pk_col, pk_value, updates)
            print(msg)


        # ------------------------------------------------------
        # 4. SCHEDULE APPOINTMENT + TREATMENT
        # ------------------------------------------------------
        elif choice == "4":
            owner_id, animal_id, vet_id, date_time = ui.get_appointment_inputs()
            t_choice = ui.choose_treatment_ui(cursor)

            new_treat = None
            if t_choice == "0":
                new_treat = ui.get_new_treatment_type_ui()

            success, result = services.schedule_appointment_and_treatment(
                cursor, db.connection,
                owner_id, animal_id, vet_id, date_time,
                t_choice, new_treat
            )

            if not success:
                print(result)     # result is error message
            else:
                ui.print_appointment_result(result)

        # ------------------------------------------------------
        # 5. TREATMENT SUMMARY
        # ------------------------------------------------------
        elif choice == "5":
            owner_id = input("OwnerID: ")
            animal_id = input("AnimalID: ")

            success, rows = services.get_appointment_summary(cursor, owner_id, animal_id)

            if not success:
                print(rows)  # rows contains error string
            else:
                ui.print_query_results(cursor, rows)

        # ------------------------------------------------------
        # 6. CANCEL APPOINTMENT
        # ------------------------------------------------------
        elif choice == "6":
            appt_id, animal_id = ui.get_cancel_appt_inputs()
            success, msg = services.cancel_appointment(cursor, db.connection, appt_id, animal_id)
            print(msg)

        # ------------------------------------------------------
        # 7. LIST PETS BY OWNER
        # ------------------------------------------------------
        elif choice == "7":
            owner_id = input("OwnerID: ")
            pets = services.list_pets_by_owner(cursor, owner_id)
            if pets is None:
                print("Owner not found.")
            else:
                ui.print_query_results(cursor, pets)

        # ------------------------------------------------------
        # 8. EXIT
        # ------------------------------------------------------
        elif choice == "8":
            print("Goodbye.")
            break

        else:
            print("Invalid selection.")

    db.close()


if __name__ == "__main__":
    main()
