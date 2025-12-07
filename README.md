# 🐾 Vet Clinic Management System  
*A Python + MySQL Console Application using Clean Layered Architecture*

---

## 📌 Overview

This project is a console-based management system for a veterinary clinic.  
It allows users to:

- View database tables  
- Insert or update rows  
- Schedule appointments **with treatments automatically linked**  
- Display treatment summaries  
- Cancel appointments  
- List pets by owner  

The project is structured using a **clean, professional separation of concerns**:

```
UI (View) 
→ Services (Business Logic) 
→ Query Layer (SQL) 
→ Database Connection Layer 
→ MySQL Database
```

Each file performs exactly one role, making the program modular, testable, and scalable.

---

## 🚀 Running the Program

### 1️⃣ Install dependencies

```bash
pip install mysql-connector-python
```

### 2️⃣ Start MySQL and ensure the `vetclinic` database exists.

### 3️⃣ Run the application:

```bash
python main.py
```

### 4️⃣ Enter database credentials (defaults provided):

- Host: `localhost`  
- User: `root`  
- Database: `vetclinic`  
- Password: `Panthers1!`

---

## 📁 Project Structure

```
VetClinic/
│
├── main.py          # Application controller & menu
├── ui.py            # Input/output & formatting
├── services.py      # Business rules & workflow logic
├── query.py         # Pure SQL queries (no logic)
├── Database.py      # MySQL connection class
└── README.md
```

---

# 🧠 Architecture Breakdown

## 🟦 main.py — The Controller Layer

Coordinates:
- menu display  
- user choices  
- calling services and UI  
- routing actions  

📌 **Important:**  
No SQL. No validation. No printing beyond menu text.

---

## 🟩 ui.py — User Input & Output (View Layer)

Handles:
- Getting user input  
- Table selection  
- Pretty table printing  
- Displaying formatted appointment results  

📌 Never touches SQL.  
📌 Only interacts with `services.py`.

---

## 🟨 services.py — Business Logic Layer

Responsible for:
- Validating owners, animals, vets  
- Sequencing multi-step operations (e.g., create appointment THEN create treatment)  
- Calling query layer functions  
- Handling commits  
- Returning success/error messages  

📌 Contains **logic**, but **NO SQL** and **NO printing**.

---

## 🟥 query.py — SQL Layer (Model / Data Access)

Contains ONLY:
- `SELECT`  
- `INSERT`  
- `UPDATE`  
- `DELETE`  
- Joins  
- Table descriptions  

📌 No business rules.  
📌 No printing.  
📌 No commits.

---

## 🟪 Database.py — Connection Handler

Establishes:
- MySQL connection  
- Cursor creation  
- Transaction commits  
- Connection closing  

This isolates MySQL details from the rest of the system.

---

# 🔄 Data Flow Diagram

```
User
 ↓
UI.py              (input/output only)
 ↓
main.py            (controller)
 ↓
services.py        (business rules / validation)
 ↓
query.py           (SQL only)
 ↓
Database.py        (connection + cursor)
 ↓
MySQL
```

---

# 🧪 Example Output

## Appointment Scheduling Result

```
Appointment Scheduled Successfully
---------------------------------
Field       | Value
------------+---------------------
ApptID      | 42
DateTime    | 2025-03-01
Vet         | Dr. Nuts
Animal      | Whiskers
Treatment   | Annual Checkup
```

## Table View Output

```
ApptID | DateTime   | TreatmentType   | Vname
------------------------------------------------
42     | 2025-03-01 | Annual Checkup  | Dr. Nuts
33     | 2024-11-13 | Deworming       | Dr. Beans
```

---

# 🧾 Key Features

### ✔ Insert rows into any non-restricted table  
Auto-increment columns handled automatically.

### ✔ Update rows by selecting which columns to modify

### ✔ Schedule appointment + treatment in **one transaction**

### ✔ Treatment summaries sorted by date

### ✔ Appointment cancellation removes child treatments first

### ✔ All date fields formatted cleanly for readability

---

# 🛠 Technologies Used

- **Python 3**
- **MySQL**
- **mysql-connector-python**
- Layered software architecture

---

# 📜 License

This project is for educational purposes as part of a database systems course.

---

# 🙌 Contributing

Feel free to extend the project by adding:

- More relationship logic  
- Additional reports  
- GUI wrapper  
- Web API layer  
