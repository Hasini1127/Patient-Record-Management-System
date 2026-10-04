import mysql.connector
import random
from datetime import datetime, timedelta
from config import Config

def seed_medical_data():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT patient_id, doctor_id, disease_id FROM patients WHERE status = 'Admitted'")
        admitted = cursor.fetchall()
        
        operations = [
            ("Laparoscopic Appendectomy", "Successful"),
            ("Coronary Angioplasty", "Pending Recovery"),
            ("Fracture Fixation", "Successful"),
            ("Cataract Surgery", "Successful"),
            ("Cholecystectomy", "Complications Encountered")
        ]
        
        for p in admitted:
            # Seed 2 Consultations
            for i in range(2):
                date = datetime.now() - timedelta(days=random.randint(1, 10))
                cursor.execute("""
                    INSERT INTO consultations (patient_id, doctor_id, consultation_date, symptoms, diagnosis, prescription, doctor_notes, follow_up_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (p['patient_id'], p['doctor_id'], date, "Routine follow up.", "Routine checkup and vitals monitoring.", "Continue prescribed medications.", "Patient is stable.", None))
            
            # Seed 1 Operation occasionally
            if random.random() > 0.5:
                op = random.choice(operations)
                date = datetime.now() - timedelta(days=random.randint(1, 5))
                cursor.execute("""
                    INSERT INTO operations (patient_id, operation_name, operation_date, doctor_id, details, outcome)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (p['patient_id'], op[0], date, p['doctor_id'], "Standard procedure under general anesthesia.", op[1]))
                
        conn.commit()
        print("Medical timeline seeded successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    seed_medical_data()
