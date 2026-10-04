import mysql.connector
from config import Config

def seed_data():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        
        diseases = [
            ("Hypertension", "Chronic high blood pressure.", "Cardiology", "Low sodium DASH diet.", "Minimum 2L water daily unless contraindicated.", "Loose, comfortable clothing.", "Moderate aerobic exercise, 30 mins/day."),
            ("Type 2 Diabetes", "Chronic condition affecting blood sugar regulation.", "Endocrinology", "Low glycemic index, carb-controlled diet.", "Adequate hydration, avoid sugary drinks.", "Comfortable shoes for foot care.", "Daily walks, stay active."),
            ("Asthma", "Respiratory condition causing airway inflammation.", "Pulmonology", "Anti-inflammatory diet, rich in antioxidants.", "Warm fluids, standard hydration.", "Avoid tight clothing around chest.", "Light exercise, avoid cold/dry air triggers."),
            ("Osteoarthritis", "Degeneration of joint cartilage.", "Orthopedics", "Anti-inflammatory diet, rich in Omega-3.", "Standard hydration.", "Easy to put on clothing, non-slip shoes.", "Low-impact exercises, swimming, physical therapy."),
            ("Migraine", "Severe, recurring headaches.", "Neurology", "Avoid trigger foods (caffeine, aged cheese).", "High hydration, 2.5L daily.", "Comfortable clothing, sunglasses if photophobic.", "Rest in a dark, quiet room during attacks."),
            ("Pneumonia", "Infection inflating air sacs in lungs.", "Pulmonology", "High protein, immune-boosting diet.", "High fluid intake to loosen mucus.", "Warm, comfortable layers.", "Bed rest, gradual return to activity."),
            ("Coronary Artery Disease", "Narrowing of the coronary arteries.", "Cardiology", "Heart-healthy, low saturated fat diet.", "Moderate hydration.", "Loose clothing, no restrictive belts.", "Cardiac rehab program, monitored walking."),
            ("Chronic Kidney Disease", "Gradual loss of kidney function.", "Nephrology", "Low potassium, low phosphorus, low protein.", "Strictly monitored fluid intake.", "Comfortable, non-restrictive clothing.", "Light activity to avoid fatigue."),
            ("Gastric Ulcer", "Sores in the stomach lining.", "Gastroenterology", "Bland diet, avoid spicy, acidic, or fried foods.", "Frequent small sips of water.", "Loose waistbands.", "Normal mobility, avoid heavy lifting."),
            ("Anemia", "Lack of enough healthy red blood cells.", "Hematology", "Iron-rich diet (spinach, red meat, beans).", "Standard hydration.", "Warm clothing (patients may feel cold easily).", "Light mobility, avoid overexertion to prevent fainting.")
        ]
        
        # Insert diseases
        for d in diseases:
            cursor.execute("SELECT disease_id FROM diseases WHERE disease_name = %s", (d[0],))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO diseases (disease_name, description, department) VALUES (%s, %s, %s)", (d[0], d[1], d[2]))
        
        conn.commit()
        
        # Now auto-generate care plans for all patients if they don't have one
        cursor.execute("""
            SELECT p.patient_id, d.disease_name 
            FROM patients p 
            JOIN diseases d ON p.disease_id = d.disease_id
        """)
        patients = cursor.fetchall()
        
        for p in patients:
            cursor.execute("SELECT plan_id FROM care_plans WHERE patient_id = %s", (p['patient_id'],))
            if not cursor.fetchone():
                # Find matching disease plan
                matching_d = next((x for x in diseases if x[0] == p['disease_name']), None)
                if matching_d:
                    cursor.execute("""
                        INSERT INTO care_plans (patient_id, diet_plan, hydration_plan, clothing_comfort, mobility_status)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (p['patient_id'], matching_d[3], matching_d[4], matching_d[5], matching_d[6]))
                else:
                    cursor.execute("""
                        INSERT INTO care_plans (patient_id, diet_plan, hydration_plan, clothing_comfort, mobility_status)
                        VALUES (%s, 'Standard balanced diet', 'Standard intake', 'Hospital Gown', 'Independent')
                    """, (p['patient_id'],))
                    
        conn.commit()
        print("Diseases and Care Plans seeded successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    seed_data()
