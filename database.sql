CREATE DATABASE IF NOT EXISTS patient_record_management;
USE patient_record_management;

-- 1. diseases table
CREATE TABLE IF NOT EXISTS diseases (
    disease_id INT AUTO_INCREMENT PRIMARY KEY,
    disease_name VARCHAR(100) NOT NULL,
    description TEXT,
    department VARCHAR(100) NOT NULL
);

-- 2. wards table
CREATE TABLE IF NOT EXISTS wards (
    ward_id INT AUTO_INCREMENT PRIMARY KEY,
    ward_number VARCHAR(20) NOT NULL UNIQUE,
    ward_type VARCHAR(50) NOT NULL,
    total_beds INT NOT NULL,
    available_beds INT NOT NULL
);

-- 3. doctors table
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15),
    email VARCHAR(100),
    experience INT,
    department VARCHAR(100) NOT NULL
);

-- 4. patients table
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    phone_number VARCHAR(15),
    email VARCHAR(100),
    address TEXT,
    blood_group VARCHAR(5),
    disease_id INT,
    doctor_id INT,
    ward_id INT,
    room_number VARCHAR(20),
    admission_date DATE,
    discharge_date DATE,
    status ENUM('Admitted', 'Discharged') NOT NULL DEFAULT 'Admitted',
    FOREIGN KEY (disease_id) REFERENCES diseases(disease_id) ON DELETE SET NULL,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE SET NULL,
    FOREIGN KEY (ward_id) REFERENCES wards(ward_id) ON DELETE SET NULL
);

-- 5. consultations table
CREATE TABLE IF NOT EXISTS consultations (
    consultation_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    consultation_date DATE NOT NULL,
    symptoms TEXT,
    diagnosis TEXT,
    prescription TEXT,
    doctor_notes TEXT,
    follow_up_date DATE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
);

-- Sample Data Insertion

INSERT INTO diseases (disease_name, description, department) VALUES 
('Hypertension', 'High blood pressure condition', 'Cardiology'),
('Migraine', 'Severe recurring headaches', 'Neurology'),
('Type 2 Diabetes', 'Chronic condition affecting insulin', 'Endocrinology'),
('Asthma', 'Respiratory condition causing difficulty breathing', 'Pulmonology'),
('Osteoarthritis', 'Degeneration of joint cartilage', 'Orthopedics');

INSERT INTO wards (ward_number, ward_type, total_beds, available_beds) VALUES 
('W-101', 'General', 20, 18),
('W-102', 'ICU', 10, 5),
('W-103', 'Emergency', 15, 10),
('W-104', 'Private', 5, 2),
('W-105', 'Semi-Private', 10, 8);

INSERT INTO doctors (doctor_name, specialization, phone_number, email, experience, department) VALUES 
('Dr. Alice Smith', 'Cardiologist', '9876543210', 'alice.smith@hospital.com', 12, 'Cardiology'),
('Dr. Bob Jones', 'Neurologist', '9876543211', 'bob.jones@hospital.com', 15, 'Neurology'),
('Dr. Charlie Brown', 'General Physician', '9876543212', 'charlie.brown@hospital.com', 8, 'General Medicine'),
('Dr. Diana Prince', 'Orthopedic', '9876543213', 'diana.prince@hospital.com', 10, 'Orthopedics'),
('Dr. Edward Cullen', 'Pediatrician', '9876543214', 'edward.cullen@hospital.com', 5, 'Pediatrics');

INSERT INTO patients (patient_name, age, gender, phone_number, email, address, blood_group, disease_id, doctor_id, ward_id, room_number, admission_date, status) VALUES 
('John Doe', 45, 'Male', '1112223333', 'john@example.com', '123 Elm St', 'O+', 1, 1, 1, '101A', '2023-10-01', 'Admitted'),
('Jane Smith', 32, 'Female', '2223334444', 'jane@example.com', '456 Oak St', 'A-', 2, 2, 4, '401', '2023-10-05', 'Admitted'),
('Michael Johnson', 60, 'Male', '3334445555', 'michael@example.com', '789 Pine St', 'B+', 3, 3, 1, '101B', '2023-10-10', 'Admitted'),
('Emily Davis', 25, 'Female', '4445556666', 'emily@example.com', '321 Maple St', 'AB+', 4, 3, 3, '301', '2023-10-15', 'Admitted'),
('Robert Wilson', 50, 'Male', '5556667777', 'robert@example.com', '654 Birch St', 'O-', 5, 4, 5, '501', '2023-10-20', 'Admitted'),
('Sarah Miller', 40, 'Female', '6667778888', 'sarah@example.com', '987 Cedar St', 'A+', 1, 1, 2, '201', '2023-10-25', 'Admitted'),
('David Taylor', 55, 'Male', '7778889999', 'david@example.com', '159 Walnut St', 'B-', 3, 3, NULL, NULL, '2023-09-01', 'Discharged'),
('Linda Anderson', 28, 'Female', '8889990000', 'linda@example.com', '753 Cherry St', 'O+', 2, 2, NULL, NULL, '2023-09-15', 'Discharged');

-- Note: In patients above, David and Linda are discharged, so their discharge dates should ideally be set. Let's update them.
UPDATE patients SET discharge_date = '2023-09-10' WHERE patient_id = 7;
UPDATE patients SET discharge_date = '2023-09-20' WHERE patient_id = 8;

INSERT INTO consultations (patient_id, doctor_id, consultation_date, symptoms, diagnosis, prescription, doctor_notes, follow_up_date) VALUES 
(1, 1, '2023-10-02', 'High blood pressure, dizziness', 'Hypertension Stage 2', 'Amlodipine 5mg', 'Monitor BP daily', '2023-10-16'),
(2, 2, '2023-10-06', 'Severe headache, nausea', 'Migraine without aura', 'Sumatriptan 50mg', 'Avoid bright lights', '2023-10-20'),
(3, 3, '2023-10-11', 'Frequent urination, thirst', 'Type 2 Diabetes', 'Metformin 500mg', 'Diet control required', '2023-11-11'),
(4, 3, '2023-10-16', 'Shortness of breath, wheezing', 'Asthma exacerbation', 'Albuterol inhaler', 'Keep inhaler handy', '2023-10-30'),
(5, 4, '2023-10-21', 'Knee joint pain', 'Osteoarthritis of knee', 'Ibuprofen 400mg', 'Physiotherapy recommended', '2023-11-21'),
(6, 1, '2023-10-26', 'Chest pain, elevated BP', 'Hypertensive crisis', 'IV Labetalol', 'Admitted to ICU for observation', '2023-11-02'),
(7, 3, '2023-09-02', 'Fatigue, blurred vision', 'Type 2 Diabetes initial diagnosis', 'Metformin 500mg', 'Follow up in 1 month', '2023-10-02'),
(8, 2, '2023-09-16', 'Throbbing headache', 'Migraine', 'Naproxen 500mg', 'Rest in dark room', '2023-09-30');

-- 6. users table (For Authentication & Authorization)
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Doctor', 'Receptionist') NOT NULL,
    doctor_id INT NULL,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE SET NULL
);

-- 7. audit_logs table (For DBMS Viva Standout Feature)
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(50),
    table_name VARCHAR(50),
    record_id INT,
    old_data TEXT,
    new_data TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(50)
);

-- Triggers for Audit Logs
DELIMITER //

DROP TRIGGER IF EXISTS after_patient_insert//
CREATE TRIGGER after_patient_insert
AFTER INSERT ON patients
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('INSERT', 'patients', NEW.patient_id, NULL, JSON_OBJECT('patient_name', NEW.patient_name, 'age', NEW.age, 'gender', NEW.gender, 'status', NEW.status), IFNULL(@current_username, 'System'));
END;//

DROP TRIGGER IF EXISTS after_patient_update//
CREATE TRIGGER after_patient_update
AFTER UPDATE ON patients
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('UPDATE', 'patients', NEW.patient_id, JSON_OBJECT('patient_name', OLD.patient_name, 'age', OLD.age, 'gender', OLD.gender, 'status', OLD.status, 'ward_id', OLD.ward_id, 'disease_id', OLD.disease_id), JSON_OBJECT('patient_name', NEW.patient_name, 'age', NEW.age, 'gender', NEW.gender, 'status', NEW.status, 'ward_id', NEW.ward_id, 'disease_id', NEW.disease_id), IFNULL(@current_username, 'System'));
END;//

DROP TRIGGER IF EXISTS after_patient_delete//
CREATE TRIGGER after_patient_delete
AFTER DELETE ON patients
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('DELETE', 'patients', OLD.patient_id, JSON_OBJECT('patient_name', OLD.patient_name, 'status', OLD.status), NULL, IFNULL(@current_username, 'System'));
END;//

-- Doctors
DROP TRIGGER IF EXISTS after_doctor_insert//
CREATE TRIGGER after_doctor_insert
AFTER INSERT ON doctors
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('INSERT', 'doctors', NEW.doctor_id, NULL, JSON_OBJECT('doctor_name', NEW.doctor_name, 'specialization', NEW.specialization), IFNULL(@current_username, 'System'));
END;//

DROP TRIGGER IF EXISTS after_doctor_update//
CREATE TRIGGER after_doctor_update
AFTER UPDATE ON doctors
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('UPDATE', 'doctors', NEW.doctor_id, JSON_OBJECT('doctor_name', OLD.doctor_name, 'specialization', OLD.specialization), JSON_OBJECT('doctor_name', NEW.doctor_name, 'specialization', NEW.specialization), IFNULL(@current_username, 'System'));
END;//

DROP TRIGGER IF EXISTS after_doctor_delete//
CREATE TRIGGER after_doctor_delete
AFTER DELETE ON doctors
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('DELETE', 'doctors', OLD.doctor_id, JSON_OBJECT('doctor_name', OLD.doctor_name, 'specialization', OLD.specialization), NULL, IFNULL(@current_username, 'System'));
END;//

-- Diseases
DROP TRIGGER IF EXISTS after_disease_insert//
CREATE TRIGGER after_disease_insert
AFTER INSERT ON diseases
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('INSERT', 'diseases', NEW.disease_id, NULL, JSON_OBJECT('disease_name', NEW.disease_name, 'department', NEW.department), IFNULL(@current_username, 'System'));
END;//

DROP TRIGGER IF EXISTS after_disease_update//
CREATE TRIGGER after_disease_update
AFTER UPDATE ON diseases
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('UPDATE', 'diseases', NEW.disease_id, JSON_OBJECT('disease_name', OLD.disease_name, 'department', OLD.department), JSON_OBJECT('disease_name', NEW.disease_name, 'department', NEW.department), IFNULL(@current_username, 'System'));
END;//

DROP TRIGGER IF EXISTS after_disease_delete//
CREATE TRIGGER after_disease_delete
AFTER DELETE ON diseases
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('DELETE', 'diseases', OLD.disease_id, JSON_OBJECT('disease_name', OLD.disease_name, 'department', OLD.department), NULL, IFNULL(@current_username, 'System'));
END;//

-- Wards
DROP TRIGGER IF EXISTS after_ward_insert//
CREATE TRIGGER after_ward_insert
AFTER INSERT ON wards
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('INSERT', 'wards', NEW.ward_id, NULL, JSON_OBJECT('ward_number', NEW.ward_number, 'total_beds', NEW.total_beds, 'available_beds', NEW.available_beds), IFNULL(@current_username, 'System'));
END;//

DROP TRIGGER IF EXISTS after_ward_update//
CREATE TRIGGER after_ward_update
AFTER UPDATE ON wards
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('UPDATE', 'wards', NEW.ward_id, JSON_OBJECT('ward_number', OLD.ward_number, 'total_beds', OLD.total_beds, 'available_beds', OLD.available_beds), JSON_OBJECT('ward_number', NEW.ward_number, 'total_beds', NEW.total_beds, 'available_beds', NEW.available_beds), IFNULL(@current_username, 'System'));
END;//

DROP TRIGGER IF EXISTS after_ward_delete//
CREATE TRIGGER after_ward_delete
AFTER DELETE ON wards
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('DELETE', 'wards', OLD.ward_id, JSON_OBJECT('ward_number', OLD.ward_number, 'total_beds', OLD.total_beds), NULL, IFNULL(@current_username, 'System'));
END;//

-- Consultations
DROP TRIGGER IF EXISTS after_consultation_insert//
CREATE TRIGGER after_consultation_insert
AFTER INSERT ON consultations
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('INSERT', 'consultations', NEW.consultation_id, NULL, JSON_OBJECT('patient_id', NEW.patient_id, 'doctor_id', NEW.doctor_id, 'diagnosis', NEW.diagnosis), IFNULL(@current_username, 'System'));
END;//

DROP TRIGGER IF EXISTS after_consultation_update//
CREATE TRIGGER after_consultation_update
AFTER UPDATE ON consultations
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('UPDATE', 'consultations', NEW.consultation_id, JSON_OBJECT('patient_id', OLD.patient_id, 'doctor_id', OLD.doctor_id, 'diagnosis', OLD.diagnosis), JSON_OBJECT('patient_id', NEW.patient_id, 'doctor_id', NEW.doctor_id, 'diagnosis', NEW.diagnosis), IFNULL(@current_username, 'System'));
END;//

DROP TRIGGER IF EXISTS after_consultation_delete//
CREATE TRIGGER after_consultation_delete
AFTER DELETE ON consultations
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
    VALUES ('DELETE', 'consultations', OLD.consultation_id, JSON_OBJECT('patient_id', OLD.patient_id, 'doctor_id', OLD.doctor_id, 'diagnosis', OLD.diagnosis), NULL, IFNULL(@current_username, 'System'));
END;//

DELIMITER ;
