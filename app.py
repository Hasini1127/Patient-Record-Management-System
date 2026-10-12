from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import json

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME'],
            port=app.config['DB_PORT'],
            ssl_disabled=False
        )
        if 'username' in session:
            cursor = conn.cursor()
            cursor.execute("SET @current_username = %s", (session['username'],))
            cursor.close()
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# ==========================================
# AUTHENTICATION & ROLES
# ==========================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['doctor_id'] = user['doctor_id']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = 'Receptionist'  # Default role for new signups
        doctor_id = None
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            flash('Username or Email already exists!', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, email, password_hash, role, doctor_id) VALUES (%s, %s, %s, %s, %s)",
                       (username, email, hashed_password, role, doctor_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# ==========================================
# DASHBOARD
# ==========================================

@app.route('/')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get total counts
    cursor.execute("SELECT COUNT(*) as count FROM patients")
    total_patients = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM doctors")
    total_doctors = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM diseases")
    total_diseases = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM wards")
    total_wards = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status='Admitted'")
    admitted_patients = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status='Discharged'")
    discharged_patients = cursor.fetchone()['count']
    
    # Recent patients
    cursor.execute("""
        SELECT p.patient_id, p.patient_name, p.status, d.doctor_name, w.ward_number 
        FROM patients p
        LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
        LEFT JOIN wards w ON p.ward_id = w.ward_id
        ORDER BY p.patient_id DESC LIMIT 5
    """)
    recent_patients = cursor.fetchall()

    # Chart Data: Patients per Ward
    cursor.execute("""
        SELECT w.ward_number, COUNT(p.patient_id) as patient_count 
        FROM wards w
        LEFT JOIN patients p ON w.ward_id = p.ward_id AND p.status = 'Admitted'
        GROUP BY w.ward_id
    """)
    ward_stats = cursor.fetchall()
    chart_ward_labels = [w['ward_number'] for w in ward_stats]
    chart_ward_data = [w['patient_count'] for w in ward_stats]

    # Analytics: Disease-wise stats
    cursor.execute("""
        SELECT d.disease_name, COUNT(p.patient_id) as p_count 
        FROM diseases d 
        JOIN patients p ON d.disease_id = p.disease_id 
        GROUP BY d.disease_id ORDER BY p_count DESC LIMIT 5
    """)
    disease_stats = cursor.fetchall()

    # Analytics: Doctor-wise stats
    cursor.execute("""
        SELECT d.doctor_name, COUNT(p.patient_id) as p_count 
        FROM doctors d 
        JOIN patients p ON d.doctor_id = p.doctor_id 
        WHERE p.status = 'Admitted'
        GROUP BY d.doctor_id ORDER BY p_count DESC LIMIT 5
    """)
    doctor_stats = cursor.fetchall()

    # Smart Alerts
    cursor.execute("SELECT COUNT(*) as count FROM consultations WHERE follow_up_date = CURDATE()")
    follow_ups_today = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM wards WHERE available_beds = 0")
    full_wards = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM wards WHERE available_beds > 0 AND available_beds <= 2")
    low_bed_wards = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status='Admitted' AND admission_date < DATE_SUB(CURDATE(), INTERVAL 7 DAY)")
    long_admissions = cursor.fetchone()['count']
    
    cursor.close()
    conn.close()
    
    return render_template('index.html', 
                           total_patients=total_patients,
                           total_doctors=total_doctors,
                           total_diseases=total_diseases,
                           total_wards=total_wards,
                           admitted_patients=admitted_patients,
                           discharged_patients=discharged_patients,
                           recent_patients=recent_patients,
                           chart_ward_labels=json.dumps(chart_ward_labels),
                           chart_ward_data=json.dumps(chart_ward_data),
                           disease_stats=disease_stats,
                           doctor_stats=doctor_stats,
                           alerts={'follow_ups': follow_ups_today, 'full_wards': full_wards, 'low_beds': low_bed_wards, 'long_admissions': long_admissions})

# ==========================================
# PATIENTS
# ==========================================

@app.route('/patients')
@login_required
def patients():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    gender_filter = request.args.get('gender', '')
    doctor_filter = request.args.get('doctor_id', '')
    disease_filter = request.args.get('disease_id', '')
    ward_filter = request.args.get('ward_id', '')
    blood_group_filter = request.args.get('blood_group', '')
    admission_date_filter = request.args.get('admission_date', '')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT p.*, d.doctor_name, d.specialization, ds.disease_name, w.ward_number 
        FROM patients p
        LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
        LEFT JOIN diseases ds ON p.disease_id = ds.disease_id
        LEFT JOIN wards w ON p.ward_id = w.ward_id
        WHERE 1=1
    """
    params = []
    
    if search:
        query += " AND (p.patient_name LIKE %s OR p.phone_number LIKE %s OR d.doctor_name LIKE %s OR w.ward_number LIKE %s OR ds.disease_name LIKE %s OR p.patient_id LIKE %s)"
        like_search = f"%{search}%"
        params.extend([like_search] * 6)
        
    if status_filter:
        query += " AND p.status = %s"
        params.append(status_filter)
        
    if gender_filter:
        query += " AND p.gender = %s"
        params.append(gender_filter)
        
    if doctor_filter:
        query += " AND p.doctor_id = %s"
        params.append(doctor_filter)
        
    if disease_filter:
        query += " AND p.disease_id = %s"
        params.append(disease_filter)
        
    if ward_filter:
        query += " AND p.ward_id = %s"
        params.append(ward_filter)
        
    if blood_group_filter:
        query += " AND p.blood_group = %s"
        params.append(blood_group_filter)
        
    if admission_date_filter:
        query += " AND p.admission_date = %s"
        params.append(admission_date_filter)
        
    query += " ORDER BY p.patient_id DESC"
    cursor.execute(query, tuple(params))
    patients = cursor.fetchall()

    # Fetch options for filters
    cursor.execute("SELECT doctor_id, doctor_name FROM doctors")
    doctors = cursor.fetchall()
    
    cursor.execute("SELECT disease_id, disease_name FROM diseases")
    diseases = cursor.fetchall()
    
    cursor.execute("SELECT ward_id, ward_number FROM wards")
    wards = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('patients.html', patients=patients, doctors=doctors, diseases=diseases, wards=wards)


@app.route('/patients/add', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Receptionist')
def add_patient():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        blood_group = request.form['blood_group']
        disease_id = request.form['disease_id'] or None
        doctor_id = request.form['doctor_id'] or None
        ward_id = request.form['ward_id'] or None
        room_number = request.form['room_number']
        admission_date = request.form['admission_date'] or None
        status = request.form['status']
        
        if not name or not age or not gender:
            flash('Name, Age, and Gender are required fields!', 'error')
            return redirect(url_for('add_patient'))
            
        if status == 'Admitted' and ward_id:
            cursor.execute("SELECT available_beds FROM wards WHERE ward_id = %s", (ward_id,))
            ward = cursor.fetchone()
            if ward and ward['available_beds'] <= 0:
                flash('Selected ward has no available beds!', 'error')
                return redirect(url_for('add_patient'))
            cursor.execute("UPDATE wards SET available_beds = available_beds - 1 WHERE ward_id = %s", (ward_id,))
            
        cursor.execute("""
            INSERT INTO patients (patient_name, age, gender, phone_number, email, address, blood_group, disease_id, doctor_id, ward_id, room_number, admission_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, age, gender, phone, email, address, blood_group, disease_id, doctor_id, ward_id, room_number, admission_date, status))
        patient_id = cursor.lastrowid
        
        # Auto-generate Care Plan
        if disease_id:
            # We fetch the disease name/details. However, we hardcoded disease plans in the seed, 
            # let's just generate a standard one here that they can edit, or fetch the disease name to match.
            cursor.execute("SELECT disease_name FROM diseases WHERE disease_id = %s", (disease_id,))
            disease_data = cursor.fetchone()
            disease_name = disease_data['disease_name'] if disease_data else ""
            
            # Simple matching or default
            diet_plan = "Standard balanced diet"
            hydration = "Standard intake"
            clothing = "Hospital Gown"
            mobility = "Independent"
            
            if "Diabetes" in disease_name:
                diet_plan = "Low glycemic index, carb-controlled diet."
                mobility = "Daily walks, stay active."
            elif "Hypertension" in disease_name:
                diet_plan = "Low sodium DASH diet."
            elif "Migraine" in disease_name:
                diet_plan = "Avoid trigger foods."
                clothing = "Comfortable clothing, sunglasses if photophobic."
                mobility = "Rest in a dark, quiet room during attacks."
                
            cursor.execute("""
                INSERT INTO care_plans (patient_id, diet_plan, hydration_plan, clothing_comfort, mobility_status)
                VALUES (%s, %s, %s, %s, %s)
            """, (patient_id, diet_plan, hydration, clothing, mobility))
        
        conn.commit()
        flash('Patient added successfully! Initial care plan auto-generated.', 'success')
        return redirect(url_for('patients'))
        
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    cursor.execute("SELECT * FROM diseases")
    diseases = cursor.fetchall()
    cursor.execute("SELECT * FROM wards WHERE available_beds > 0")
    wards = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('add_patient.html', doctors=doctors, diseases=diseases, wards=wards)

@app.route('/patients/view/<int:id>')
@login_required
def view_patient(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.*, d.doctor_name, d.specialization, ds.disease_name, ds.description as disease_desc, w.ward_number, w.ward_type
        FROM patients p
        LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
        LEFT JOIN diseases ds ON p.disease_id = ds.disease_id
        LEFT JOIN wards w ON p.ward_id = w.ward_id
        WHERE p.patient_id = %s
    """, (id,))
    patient = cursor.fetchone()
    
    if not patient:
        flash('Patient not found!', 'error')
        return redirect(url_for('patients'))
        
    cursor.execute("""
        SELECT c.*, d.doctor_name 
        FROM consultations c
        LEFT JOIN doctors d ON c.doctor_id = d.doctor_id
        WHERE c.patient_id = %s
        ORDER BY c.consultation_date DESC
    """, (id,))
    consultations = cursor.fetchall()
    
    # Fetch Care Plans
    cursor.execute("SELECT * FROM care_plans WHERE patient_id = %s ORDER BY created_at DESC LIMIT 1", (id,))
    care_plan = cursor.fetchone()
    
    # Fetch Operations
    cursor.execute("""
        SELECT o.*, d.doctor_name as surgeon_name 
        FROM operations o
        LEFT JOIN doctors d ON o.doctor_id = d.doctor_id
        WHERE o.patient_id = %s
        ORDER BY o.operation_date DESC
    """, (id,))
    operations = cursor.fetchall()
    
    # Combine Consultations and Operations into a Timeline
    timeline = []
    for c in consultations:
        timeline.append({
            'type': 'consultation',
            'date': c['consultation_date'],
            'doctor': c['doctor_name'],
            'details': c['diagnosis'],
            'id': c['consultation_id']
        })
    for o in operations:
        timeline.append({
            'type': 'operation',
            'date': o['operation_date'],
            'doctor': o['surgeon_name'],
            'details': o['operation_name'],
            'id': o['operation_id']
        })
        
    # Sort timeline by date descending
    timeline.sort(key=lambda x: x['date'], reverse=True)
    
    cursor.close()
    conn.close()
    return render_template('patient_details.html', patient=patient, timeline=timeline, care_plan=care_plan)

@app.route('/patients/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Receptionist', 'Doctor')
def edit_patient(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        # (Same update logic as before...)
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        blood_group = request.form['blood_group']
        disease_id = request.form['disease_id'] or None
        doctor_id = request.form['doctor_id'] or None
        ward_id = request.form['ward_id'] or None
        room_number = request.form['room_number']
        admission_date = request.form['admission_date'] or None
        discharge_date = request.form['discharge_date'] or None
        status = request.form['status']
        
        cursor.execute("SELECT ward_id, status FROM patients WHERE patient_id = %s", (id,))
        old_patient = cursor.fetchone()
        
        if old_patient['ward_id'] != (int(ward_id) if ward_id else None) or old_patient['status'] != status:
            if old_patient['ward_id'] and old_patient['status'] == 'Admitted':
                cursor.execute("UPDATE wards SET available_beds = available_beds + 1 WHERE ward_id = %s", (old_patient['ward_id'],))
            if ward_id and status == 'Admitted':
                cursor.execute("UPDATE wards SET available_beds = available_beds - 1 WHERE ward_id = %s", (ward_id,))
        
        cursor.execute("""
            UPDATE patients SET 
            patient_name=%s, age=%s, gender=%s, phone_number=%s, email=%s, address=%s, blood_group=%s,
            disease_id=%s, doctor_id=%s, ward_id=%s, room_number=%s, admission_date=%s, discharge_date=%s, status=%s
            WHERE patient_id=%s
        """, (name, age, gender, phone, email, address, blood_group, disease_id, doctor_id, ward_id, room_number, admission_date, discharge_date, status, id))
        conn.commit()
        flash('Patient updated successfully! Audit log created automatically.', 'success')
        return redirect(url_for('patients'))
        
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (id,))
    patient = cursor.fetchone()
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    cursor.execute("SELECT * FROM diseases")
    diseases = cursor.fetchall()
    cursor.execute("SELECT * FROM wards")
    wards = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('edit_patient.html', patient=patient, doctors=doctors, diseases=diseases, wards=wards)

@app.route('/patients/delete/<int:id>')
@login_required
@roles_required('Admin')
def delete_patient(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT ward_id, status FROM patients WHERE patient_id = %s", (id,))
    patient = cursor.fetchone()
    if patient and patient['ward_id'] and patient['status'] == 'Admitted':
        cursor.execute("UPDATE wards SET available_beds = available_beds + 1 WHERE ward_id = %s", (patient['ward_id'],))
        
    cursor.execute("DELETE FROM patients WHERE patient_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Patient deleted successfully! Audit log created automatically.', 'success')
    return redirect(url_for('patients'))

@app.route('/patient/<int:id>/discharge')
@login_required
def discharge_summary(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get Patient Details
    cursor.execute("""
        SELECT p.*, d.doctor_name, d.specialization, ds.disease_name, w.ward_number 
        FROM patients p
        LEFT JOIN doctors d ON p.doctor_id = d.doctor_id
        LEFT JOIN diseases ds ON p.disease_id = ds.disease_id
        LEFT JOIN wards w ON p.ward_id = w.ward_id
        WHERE p.patient_id = %s
    """, (id,))
    patient = cursor.fetchone()
    
    if not patient:
        flash('Patient not found!', 'error')
        return redirect(url_for('patients'))
        
    # Get latest consultation
    cursor.execute("""
        SELECT * FROM consultations 
        WHERE patient_id = %s 
        ORDER BY consultation_date DESC LIMIT 1
    """, (id,))
    latest_consultation = cursor.fetchone()
    
    # Get care plan
    cursor.execute("SELECT * FROM care_plans WHERE patient_id = %s ORDER BY created_at DESC LIMIT 1", (id,))
    care_plan = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    
    return render_template('discharge_summary.html', patient=patient, latest_consultation=latest_consultation, care_plan=care_plan, current_date=current_date)

# ==========================================
# DOCTORS
# ==========================================

@app.route('/doctors')
@login_required
@roles_required('Admin')
def doctors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            d.*,
            COUNT(DISTINCT p.patient_id) as patient_count,
            COUNT(DISTINCT c.consultation_id) as consultation_count
        FROM doctors d
        LEFT JOIN patients p ON d.doctor_id = p.doctor_id AND p.status = 'Admitted'
        LEFT JOIN consultations c ON d.doctor_id = c.doctor_id
        GROUP BY d.doctor_id
        ORDER BY d.doctor_id DESC
    """)
    doctors = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('doctors.html', doctors=doctors)

@app.route('/doctors/add', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def add_doctor():
    if request.method == 'POST':
        # Code remains same
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO doctors (doctor_name, specialization, phone_number, email, experience, department)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (request.form['name'], request.form['specialization'], request.form['phone'], request.form['email'], request.form['experience'], request.form['department']))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Doctor added successfully!', 'success')
        return redirect(url_for('doctors'))
    return render_template('add_doctor.html')

@app.route('/doctors/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def edit_doctor(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        cursor.execute("""
            UPDATE doctors SET 
            doctor_name=%s, specialization=%s, phone_number=%s, email=%s, experience=%s, department=%s
            WHERE doctor_id=%s
        """, (request.form['name'], request.form['specialization'], request.form['phone'], request.form['email'], request.form['experience'], request.form['department'], id))
        conn.commit()
        flash('Doctor updated successfully!', 'success')
        return redirect(url_for('doctors'))
    cursor.execute("SELECT * FROM doctors WHERE doctor_id = %s", (id,))
    doctor = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_doctor.html', doctor=doctor)

@app.route('/doctors/delete/<int:id>')
@login_required
@roles_required('Admin')
def delete_doctor(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM doctors WHERE doctor_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Doctor deleted successfully!', 'success')
    return redirect(url_for('doctors'))

# ==========================================
# DISEASES
# ==========================================

@app.route('/diseases')
@login_required
@roles_required('Admin')
def diseases():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM diseases ORDER BY disease_id DESC")
    diseases = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('diseases.html', diseases=diseases)

@app.route('/diseases/add', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def add_disease():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO diseases (disease_name, description, department) VALUES (%s, %s, %s)", 
                       (request.form['name'], request.form['description'], request.form['department']))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Disease added successfully!', 'success')
        return redirect(url_for('diseases'))
    return render_template('add_disease.html')

@app.route('/diseases/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def edit_disease(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        cursor.execute("UPDATE diseases SET disease_name=%s, description=%s, department=%s WHERE disease_id=%s", 
                       (request.form['name'], request.form['description'], request.form['department'], id))
        conn.commit()
        flash('Disease updated successfully!', 'success')
        return redirect(url_for('diseases'))
    cursor.execute("SELECT * FROM diseases WHERE disease_id = %s", (id,))
    disease = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_disease.html', disease=disease)

@app.route('/diseases/delete/<int:id>')
@login_required
@roles_required('Admin')
def delete_disease(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM diseases WHERE disease_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Disease deleted successfully!', 'success')
    return redirect(url_for('diseases'))

# ==========================================
# WARDS
# ==========================================

@app.route('/wards')
@login_required
@roles_required('Admin', 'Receptionist')
def wards():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all wards
    cursor.execute("SELECT * FROM wards ORDER BY ward_number")
    wards_list = cursor.fetchall()
    
    # Fetch all admitted patients assigned to a ward
    cursor.execute("SELECT patient_id, patient_name, ward_id FROM patients WHERE status = 'Admitted' AND ward_id IS NOT NULL")
    patients_in_wards = cursor.fetchall()
    
    # Group patients by ward_id
    ward_patients = {}
    for p in patients_in_wards:
        wid = p['ward_id']
        if wid not in ward_patients:
            ward_patients[wid] = []
        ward_patients[wid].append(p)
        
    for w in wards_list:
        w['patients'] = ward_patients.get(w['ward_id'], [])
        
    cursor.close()
    conn.close()
    return render_template('wards.html', wards=wards_list)

@app.route('/wards/add', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def add_ward():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wards WHERE ward_number = %s", (request.form['ward_number'],))
        if cursor.fetchone():
            flash('Ward number already exists!', 'error')
            return redirect(url_for('add_ward'))
        cursor.execute("INSERT INTO wards (ward_number, ward_type, total_beds, available_beds) VALUES (%s, %s, %s, %s)", 
                       (request.form['ward_number'], request.form['ward_type'], request.form['total_beds'], request.form['available_beds']))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Ward added successfully!', 'success')
        return redirect(url_for('wards'))
    return render_template('add_ward.html')

@app.route('/wards/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def edit_ward(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        cursor.execute("SELECT * FROM wards WHERE ward_number = %s AND ward_id != %s", (request.form['ward_number'], id))
        if cursor.fetchone():
            flash('Ward number already exists!', 'error')
            return redirect(url_for('edit_ward', id=id))
        cursor.execute("UPDATE wards SET ward_number=%s, ward_type=%s, total_beds=%s, available_beds=%s WHERE ward_id=%s", 
                       (request.form['ward_number'], request.form['ward_type'], request.form['total_beds'], request.form['available_beds'], id))
        conn.commit()
        flash('Ward updated successfully!', 'success')
        return redirect(url_for('wards'))
    cursor.execute("SELECT * FROM wards WHERE ward_id = %s", (id,))
    ward = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_ward.html', ward=ward)

@app.route('/wards/delete/<int:id>')
@login_required
@roles_required('Admin')
def delete_ward(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wards WHERE ward_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Ward deleted successfully!', 'success')
    return redirect(url_for('wards'))

# ==========================================
# CONSULTATIONS
# ==========================================

@app.route('/consultations')
@login_required
def consultations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT c.*, p.patient_name, d.doctor_name 
        FROM consultations c
        JOIN patients p ON c.patient_id = p.patient_id
        JOIN doctors d ON c.doctor_id = d.doctor_id
    """
    
    # If the user is a Doctor, they only see their own consultations
    if session.get('role') == 'Doctor' and session.get('doctor_id'):
        query += f" WHERE c.doctor_id = {session.get('doctor_id')}"
        
    query += " ORDER BY c.consultation_date DESC"
    
    cursor.execute(query)
    consultations = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('consultations.html', consultations=consultations)

@app.route('/consultations/add', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Doctor')
def add_consultation():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        cursor.execute("""
            INSERT INTO consultations (patient_id, doctor_id, consultation_date, symptoms, diagnosis, prescription, doctor_notes, follow_up_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (request.form['patient_id'], request.form['doctor_id'], request.form['consultation_date'], request.form['symptoms'], request.form['diagnosis'], request.form['prescription'], request.form['doctor_notes'], request.form['follow_up_date'] or None))
        conn.commit()
        flash('Consultation added successfully!', 'success')
        return redirect(url_for('consultations'))
        
    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    
    if session.get('role') == 'Doctor' and session.get('doctor_id'):
        cursor.execute("SELECT * FROM doctors WHERE doctor_id = %s", (session.get('doctor_id'),))
    else:
        cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('add_consultation.html', patients=patients, doctors=doctors)

@app.route('/consultations/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Doctor')
def edit_consultation(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        cursor.execute("""
            UPDATE consultations SET 
            patient_id=%s, doctor_id=%s, consultation_date=%s, symptoms=%s, diagnosis=%s, prescription=%s, doctor_notes=%s, follow_up_date=%s
            WHERE consultation_id=%s
        """, (request.form['patient_id'], request.form['doctor_id'], request.form['consultation_date'], request.form['symptoms'], request.form['diagnosis'], request.form['prescription'], request.form['doctor_notes'], request.form['follow_up_date'] or None, id))
        conn.commit()
        flash('Consultation updated successfully!', 'success')
        return redirect(url_for('consultations'))
        
    cursor.execute("SELECT * FROM consultations WHERE consultation_id = %s", (id,))
    consultation = cursor.fetchone()
    
    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('edit_consultation.html', consultation=consultation, patients=patients, doctors=doctors)

@app.route('/consultations/delete/<int:id>')
@login_required
@roles_required('Admin')
def delete_consultation(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM consultations WHERE consultation_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Consultation deleted successfully!', 'success')
    return redirect(url_for('consultations'))


# ==========================================
# CARE PLANS & OPERATIONS
# ==========================================

@app.route('/patients/<int:patient_id>/care-plan/add', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Doctor')
def add_care_plan(patient_id):
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO care_plans (patient_id, diet_plan, hydration_plan, clothing_comfort, mobility_status)
            VALUES (%s, %s, %s, %s, %s)
        """, (patient_id, request.form['diet'], request.form['hydration'], request.form['clothing'], request.form['mobility']))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Care Plan updated successfully!', 'success')
        return redirect(url_for('view_patient', id=patient_id))
    return render_template('add_care_plan.html', patient_id=patient_id)

@app.route('/patients/<int:patient_id>/operation/add', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Doctor')
def add_operation(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        cursor.execute("""
            INSERT INTO operations (patient_id, doctor_id, operation_name, operation_date, details, outcome)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (patient_id, request.form['doctor_id'], request.form['operation_name'], request.form['operation_date'], request.form['details'], request.form['outcome']))
        conn.commit()
        flash('Operation recorded successfully!', 'success')
        cursor.close()
        conn.close()
        return redirect(url_for('view_patient', id=patient_id))
        
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('add_operation.html', patient_id=patient_id, doctors=doctors)


# ==========================================
# AUDIT LOGS
# ==========================================

@app.route('/audit-logs')
@login_required
@roles_required('Admin')
def audit_logs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    search = request.args.get('search', '')
    action_filter = request.args.get('action', '')
    table_filter = request.args.get('table', '')
    date_filter = request.args.get('date', '')
    
    query = "SELECT * FROM audit_logs WHERE 1=1"
    params = []
    
    if search:
        query += " AND (changed_by LIKE %s OR table_name LIKE %s OR record_id LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    
    if action_filter:
        query += " AND action = %s"
        params.append(action_filter)
        
    if table_filter:
        query += " AND table_name = %s"
        params.append(table_filter)
        
    if date_filter:
        query += " AND DATE(changed_at) = %s"
        params.append(date_filter)
        
    query += " ORDER BY changed_at DESC"
    
    cursor.execute(query, tuple(params))
    logs = cursor.fetchall()
    
    cursor.execute("SELECT DISTINCT table_name FROM audit_logs WHERE table_name IS NOT NULL")
    tables = [row['table_name'] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    return render_template('audit_logs.html', logs=logs, tables=tables)

if __name__ == '__main__':
    app.run(debug=True)
