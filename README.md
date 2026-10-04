# PATIENT RECORD MANAGEMENT SYSTEM
# DBMS Laboratory Project

# Project Objective: A web-based Patient Record Management System using Flask and MySQL.

## Technologies Used
- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python Flask
- **Database**: MySQL

## Features
- Dashboard with summary statistics
- CRUD operations for Patients, Doctors, Diseases, Wards, Consultations
- Search and Filter for Patients
- View detailed patient records and consultation history
- Form validations on both frontend and backend

## Database Structure
The database (`patient_record_management`) contains 5 main tables:
1. `diseases` (disease_id, name, description, department)
2. `wards` (ward_id, ward_number, type, total_beds, available_beds)
3. `doctors` (doctor_id, name, specialization, phone, email, experience, department)
4. `patients` (patient_id, name, age, gender, contact, disease_id, doctor_id, ward_id, dates, status)
5. `consultations` (consultation_id, patient_id, doctor_id, date, symptoms, diagnosis, prescription, notes, follow_up)

## Folder Structure
```
Patient_Record_Management/
├── app.py
├── config.py
├── requirements.txt
├── database.sql
├── README.md
├── templates/
│   ├── base.html, index.html, ... (All HTML templates)
├── static/
    ├── css/style.css
    ├── js/script.js
```

## Setup Instructions

### 1. MySQL Setup
1. Open your MySQL client (e.g., MySQL Command Line Client or MySQL Workbench).
2. Create the database and tables by executing the `database.sql` script using the `source` command. Use forward slashes (`/`) for the path to avoid escape character issues:
   ```sql
   source C:/Users/hasin/College/Projects/Patient_Record_Management/database.sql;
   ```
   *Alternatively, you can just open the `database.sql` file in MySQL Workbench, copy all the text, and click the execute button.*

### 2. Python Setup
1. Open a terminal in the `Patient_Record_Management` folder.
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Database Credentials Configuration
1. Open `config.py`.
2. Enter your MySQL password in `DB_PASSWORD`. If your user is not `root`, update `DB_USER`. If your MySQL runs on a different host, update `DB_HOST`.

### 4. Run the Application
1. In the terminal, run:
   ```bash
   python app.py
   ```
2. Open your web browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

## CRUD Operations Implemented
- **Create**: Add records via the "Add [Entity]" forms.
- **Read**: View lists in the main sections, and detailed views (e.g., View Patient).
- **Update**: Edit records using the "Edit" buttons on list views.
- **Delete**: Remove records using "Delete" buttons with confirmation prompts.
