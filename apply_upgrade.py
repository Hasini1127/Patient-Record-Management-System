import mysql.connector
from config import Config

def upgrade_db():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('Admin', 'Doctor', 'Receptionist') NOT NULL,
                doctor_id INT NULL,
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE SET NULL
            )
        """)
        
        # Create audit_logs table
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
            )
        """)
        
        # Drop triggers if they exist
        cursor.execute("DROP TRIGGER IF EXISTS after_patient_update")
        cursor.execute("DROP TRIGGER IF EXISTS after_patient_delete")
        
        # Create Triggers
        cursor.execute("""
            CREATE TRIGGER after_patient_update
            AFTER UPDATE ON patients
            FOR EACH ROW
            BEGIN
                INSERT INTO audit_logs (action, table_name, record_id, old_data, new_data, changed_by)
                VALUES ('UPDATE', 'patients', NEW.patient_id, 
                        CONCAT('Status: ', OLD.status, ', Ward: ', IFNULL(OLD.ward_id, 'None')), 
                        CONCAT('Status: ', NEW.status, ', Ward: ', IFNULL(NEW.ward_id, 'None')), 
                        'System');
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER after_patient_delete
            AFTER DELETE ON patients
            FOR EACH ROW
            BEGIN
                INSERT INTO audit_logs (action, table_name, record_id, old_data, changed_by)
                VALUES ('DELETE', 'patients', OLD.patient_id, 
                        CONCAT('Name: ', OLD.patient_name), 
                        'System');
            END
        """)
        
        # Create a default admin user
        from werkzeug.security import generate_password_hash
        pwd_hash = generate_password_hash('admin123')
        
        cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", ('admin', pwd_hash, 'Admin'))
            print("Default admin user created (username: admin, password: admin123)")
            
        conn.commit()
        print("Database upgraded successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    upgrade_db()
