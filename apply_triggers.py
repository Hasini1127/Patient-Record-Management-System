import mysql.connector
from config import Config

def apply_audit_triggers():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = conn.cursor()
        
        # 1. Ensure audit_logs table exists
        cursor.execute("""
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
        """)
        print("Ensured audit_logs table exists.")
        
        triggers = [
            ("after_patient_insert", """
                CREATE TRIGGER after_patient_insert
                AFTER INSERT ON patients
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('INSERT', 'patients', NEW.patient_id, NULL, JSON_OBJECT('patient_name', NEW.patient_name, 'age', NEW.age, 'gender', NEW.gender, 'status', NEW.status), IFNULL(@current_username, 'System'));
                END;
            """),
            ("after_patient_update", """
                CREATE TRIGGER after_patient_update
                AFTER UPDATE ON patients
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('UPDATE', 'patients', NEW.patient_id, JSON_OBJECT('patient_name', OLD.patient_name, 'age', OLD.age, 'gender', OLD.gender, 'status', OLD.status, 'ward_id', OLD.ward_id, 'disease_id', OLD.disease_id), JSON_OBJECT('patient_name', NEW.patient_name, 'age', NEW.age, 'gender', NEW.gender, 'status', NEW.status, 'ward_id', NEW.ward_id, 'disease_id', NEW.disease_id), IFNULL(@current_username, 'System'));
                END;
            """),
            ("after_patient_delete", """
                CREATE TRIGGER after_patient_delete
                AFTER DELETE ON patients
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('DELETE', 'patients', OLD.patient_id, JSON_OBJECT('patient_name', OLD.patient_name, 'status', OLD.status), NULL, IFNULL(@current_username, 'System'));
                END;
            """),
            ("after_doctor_insert", """
                CREATE TRIGGER after_doctor_insert
                AFTER INSERT ON doctors
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('INSERT', 'doctors', NEW.doctor_id, NULL, JSON_OBJECT('doctor_name', NEW.doctor_name, 'specialization', NEW.specialization), IFNULL(@current_username, 'System'));
                END;
            """),
            ("after_doctor_update", """
                CREATE TRIGGER after_doctor_update
                AFTER UPDATE ON doctors
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('UPDATE', 'doctors', NEW.doctor_id, JSON_OBJECT('doctor_name', OLD.doctor_name, 'specialization', OLD.specialization), JSON_OBJECT('doctor_name', NEW.doctor_name, 'specialization', NEW.specialization), IFNULL(@current_username, 'System'));
                END;
            """),
            ("after_doctor_delete", """
                CREATE TRIGGER after_doctor_delete
                AFTER DELETE ON doctors
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('DELETE', 'doctors', OLD.doctor_id, JSON_OBJECT('doctor_name', OLD.doctor_name, 'specialization', OLD.specialization), NULL, IFNULL(@current_username, 'System'));
                END;
            """),
            ("after_disease_insert", """
                CREATE TRIGGER after_disease_insert
                AFTER INSERT ON diseases
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('INSERT', 'diseases', NEW.disease_id, NULL, JSON_OBJECT('disease_name', NEW.disease_name, 'department', NEW.department), IFNULL(@current_username, 'System'));
                END;
            """),
            ("after_disease_update", """
                CREATE TRIGGER after_disease_update
                AFTER UPDATE ON diseases
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('UPDATE', 'diseases', NEW.disease_id, JSON_OBJECT('disease_name', OLD.disease_name, 'department', OLD.department), JSON_OBJECT('disease_name', NEW.disease_name, 'department', NEW.department), IFNULL(@current_username, 'System'));
                END;
            """),
            ("after_disease_delete", """
                CREATE TRIGGER after_disease_delete
                AFTER DELETE ON diseases
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('DELETE', 'diseases', OLD.disease_id, JSON_OBJECT('disease_name', OLD.disease_name, 'department', OLD.department), NULL, IFNULL(@current_username, 'System'));
                END;
            """),
            ("after_ward_insert", """
                CREATE TRIGGER after_ward_insert
                AFTER INSERT ON wards
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('INSERT', 'wards', NEW.ward_id, NULL, JSON_OBJECT('ward_number', NEW.ward_number, 'total_beds', NEW.total_beds, 'available_beds', NEW.available_beds), IFNULL(@current_username, 'System'));
                END;
            """),
            ("after_ward_update", """
                CREATE TRIGGER after_ward_update
                AFTER UPDATE ON wards
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('UPDATE', 'wards', NEW.ward_id, JSON_OBJECT('ward_number', OLD.ward_number, 'total_beds', OLD.total_beds, 'available_beds', OLD.available_beds), JSON_OBJECT('ward_number', NEW.ward_number, 'total_beds', NEW.total_beds, 'available_beds', NEW.available_beds), IFNULL(@current_username, 'System'));
                END;
            """),
            ("after_ward_delete", """
                CREATE TRIGGER after_ward_delete
                AFTER DELETE ON wards
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('DELETE', 'wards', OLD.ward_id, JSON_OBJECT('ward_number', OLD.ward_number, 'total_beds', OLD.total_beds), NULL, IFNULL(@current_username, 'System'));
                END;
            """),
            ("after_consultation_insert", """
                CREATE TRIGGER after_consultation_insert
                AFTER INSERT ON consultations
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('INSERT', 'consultations', NEW.consultation_id, NULL, JSON_OBJECT('patient_id', NEW.patient_id, 'doctor_id', NEW.doctor_id, 'diagnosis', NEW.diagnosis), IFNULL(@current_username, 'System'));
                END;
            """),
            ("after_consultation_update", """
                CREATE TRIGGER after_consultation_update
                AFTER UPDATE ON consultations
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('UPDATE', 'consultations', NEW.consultation_id, JSON_OBJECT('patient_id', OLD.patient_id, 'doctor_id', OLD.doctor_id, 'diagnosis', OLD.diagnosis), JSON_OBJECT('patient_id', NEW.patient_id, 'doctor_id', NEW.doctor_id, 'diagnosis', NEW.diagnosis), IFNULL(@current_username, 'System'));
                END;
            """),
            ("after_consultation_delete", """
                CREATE TRIGGER after_consultation_delete
                AFTER DELETE ON consultations
                FOR EACH ROW
                BEGIN
                    INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                    VALUES ('DELETE', 'consultations', OLD.consultation_id, JSON_OBJECT('patient_id', OLD.patient_id, 'doctor_id', OLD.doctor_id, 'diagnosis', OLD.diagnosis), NULL, IFNULL(@current_username, 'System'));
                END;
            """)
        ]
        
        for name, ddl in triggers:
            try:
                cursor.execute(f"DROP TRIGGER IF EXISTS {name}")
                cursor.execute(ddl)
                print(f"Trigger {name} applied successfully.")
            except Exception as e:
                print(f"Error applying {name}: {e}")
                
        conn.commit()
        cursor.close()
        conn.close()
        print("Database updated with triggers successfully.")
        
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    apply_audit_triggers()
