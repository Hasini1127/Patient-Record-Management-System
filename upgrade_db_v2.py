import mysql.connector
from config import Config

def upgrade_db_v2():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = conn.cursor()
        
        # Create care_plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS care_plans (
                plan_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                diet_plan TEXT,
                hydration_plan TEXT,
                clothing_comfort TEXT,
                mobility_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
            )
        """)
        
        # Create operations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                operation_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                doctor_id INT NULL,
                operation_name VARCHAR(150) NOT NULL,
                operation_date DATETIME NOT NULL,
                details TEXT,
                outcome VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE SET NULL
            )
        """)
        
        conn.commit()
        print("Database upgraded successfully with Care Plans and Operations tables!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    upgrade_db_v2()
