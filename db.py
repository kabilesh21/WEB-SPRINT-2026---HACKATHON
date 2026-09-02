"""
Nexdemy Portal — MySQL Database & SMTP Email OTP Module
Handles database operations, strict role authentication, 20 default students,
faculty class management (add student, edit marks/CGPA/fees),
and live Gmail SMTP OTP dispatch for password reset via postmanmail21@gmail.com.
Credentials:
- MySQL: root / 2006 -> nexdemy_db
- SMTP: postmanmail21@gmail.com / wecwdxpwxsjoupgt (smtp.gmail.com:587)
"""

import pymysql
import hashlib
import json
import time
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '2006',
    'port': 3306,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

DB_NAME = 'nexdemy_db'

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'postmanmail21@gmail.com'
SMTP_PASS = 'wecwdxpwxsjoupgt'

OTP_STORE = {}

DEFAULT_20_STUDENTS = [
    ('Aravind Kumar S', '711522104001', 'B.E. Computer Science and Engineering', 'student1@nexdemy.edu', '+91 9876543201', 'Paid', 95, 42, 45),
    ('Abinaya R', '711522104002', 'B.E. Computer Science and Engineering', 'student2@nexdemy.edu', '+91 9876543202', 'Paid', 92, 41, 45),
    ('Balaji M', '711522104003', 'B.E. Computer Science and Engineering', 'student3@nexdemy.edu', '+91 9876543203', 'Pending', 78, 34, 45),
    ('Chandru K', '711522104004', 'B.E. Computer Science and Engineering', 'student4@nexdemy.edu', '+91 9876543204', 'Paid', 84, 38, 45),
    ('Deepika S', '711522104005', 'B.E. Computer Science and Engineering', 'student5@nexdemy.edu', '+91 9876543205', 'Paid', 94, 43, 45),
    ('Dinesh Kumar V', '711522104006', 'B.E. Computer Science and Engineering', 'student6@nexdemy.edu', '+91 9876543206', 'Pending', 69, 30, 45),
    ('Gayathri N', '711522104007', 'B.E. Computer Science and Engineering', 'student7@nexdemy.edu', '+91 9876543207', 'Paid', 88, 39, 45),
    ('Hariharan P', '711522104008', 'B.E. Computer Science and Engineering', 'student8@nexdemy.edu', '+91 9876543208', 'Paid', 82, 36, 45),
    ('Harini T', '711522104009', 'B.E. Computer Science and Engineering', 'student9@nexdemy.edu', '+91 9876543209', 'Paid', 96, 44, 45),
    ('Jeeva R', '711522104010', 'B.E. Computer Science and Engineering', 'student10@nexdemy.edu', '+91 9876543210', 'Pending', 71, 32, 45),
    ('Karthick Raja M', '711522104011', 'B.E. Computer Science and Engineering', 'student11@nexdemy.edu', '+91 9876543211', 'Paid', 86, 38, 45),
    ('Kavitha S', '711522104012', 'B.E. Computer Science and Engineering', 'student12@nexdemy.edu', '+91 9876543212', 'Paid', 93, 42, 45),
    ('Manikandan G', '711522104013', 'B.E. Computer Science and Engineering', 'student13@nexdemy.edu', '+91 9876543213', 'Paid', 80, 35, 45),
    ('Nandhini B', '711522104014', 'B.E. Computer Science and Engineering', 'student14@nexdemy.edu', '+91 9876543214', 'Paid', 90, 40, 45),
    ('Naveen Kumar S', '711522104015', 'B.E. Computer Science and Engineering', 'student15@nexdemy.edu', '+91 9876543215', 'Pending', 68, 29, 45),
    ('Pooja V', '711522104016', 'B.E. Computer Science and Engineering', 'student16@nexdemy.edu', '+91 9876543216', 'Paid', 89, 39, 45),
    ('Praveen Raj D', '711522104017', 'B.E. Computer Science and Engineering', 'student17@nexdemy.edu', '+91 9876543217', 'Paid', 83, 37, 45),
    ('Priya Dharshini R', '711522104018', 'B.E. Computer Science and Engineering', 'student18@nexdemy.edu', '+91 9876543218', 'Paid', 96, 44, 45),
    ('Ragul K', '711522104019', 'B.E. Computer Science and Engineering', 'student19@nexdemy.edu', '+91 9876543219', 'Pending', 74, 33, 45),
    ('Sneha M', '711522104020', 'B.E. Computer Science and Engineering', 'student20@nexdemy.edu', '+91 9876543220', 'Paid', 87, 39, 45)
]

def hash_password(password):
    return hashlib.sha256(f"nexdemy_salt_{password}".encode('utf-8')).hexdigest()

def get_connection(use_db=True):
    cfg = DB_CONFIG.copy()
    if use_db:
        cfg['database'] = DB_NAME
    return pymysql.connect(**cfg)

def init_db():
    try:
        conn = get_connection(use_db=False)
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.close()

        conn = get_connection(use_db=True)
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS `users` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `name` VARCHAR(150) NOT NULL,
                    `roll_no` VARCHAR(50) NOT NULL UNIQUE,
                    `dept` VARCHAR(150) NOT NULL,
                    `email` VARCHAR(150) NOT NULL UNIQUE,
                    `mobile` VARCHAR(30) NOT NULL,
                    `password_hash` VARCHAR(128) NOT NULL,
                    `role` ENUM('student', 'faculty') DEFAULT 'student',
                    `dob` VARCHAR(20) DEFAULT '2004-06-15',
                    `gender` VARCHAR(20) DEFAULT 'Male',
                    `academic_year` VARCHAR(50) DEFAULT '2024–2025',
                    `semester` INT DEFAULT 4,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS `student_marks` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `roll_no` VARCHAR(50) NOT NULL,
                    `code` VARCHAR(20) NOT NULL,
                    `title` VARCHAR(150) NOT NULL,
                    `credits` INT NOT NULL,
                    `faculty` VARCHAR(100) NOT NULL,
                    `venue` VARCHAR(50) NOT NULL,
                    `test1` INT DEFAULT 24,
                    `test2` INT DEFAULT 23,
                    `model` INT DEFAULT 48,
                    `assign` INT DEFAULT 10,
                    `total` INT DEFAULT 95,
                    `grade` VARCHAR(5) DEFAULT 'O',
                    `grade_point` INT DEFAULT 10,
                    `conducted` INT DEFAULT 45,
                    `attended` INT DEFAULT 42,
                    `exam_date` VARCHAR(30) DEFAULT '2026-05-04',
                    `session` VARCHAR(30) DEFAULT 'FN (09:30 AM)',
                    FOREIGN KEY (`roll_no`) REFERENCES `users`(`roll_no`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS `fee_ledger` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `roll_no` VARCHAR(50) NOT NULL,
                    `fee_name` VARCHAR(150) NOT NULL,
                    `amount` DECIMAL(10,2) NOT NULL,
                    `due_date` VARCHAR(30) NOT NULL,
                    `status` VARCHAR(30) DEFAULT 'Paid',
                    `txn_id` VARCHAR(50) NOT NULL,
                    `paid_date` VARCHAR(30) NOT NULL,
                    FOREIGN KEY (`roll_no`) REFERENCES `users`(`roll_no`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            conn.commit()

            # Seed Default Faculty Member
            cur.execute("SELECT id FROM users WHERE roll_no = 'STAFF01'")
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO users (name, roll_no, dept, email, mobile, password_hash, role)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    'Dr. A. Rajesh (Faculty)',
                    'STAFF01',
                    'B.E. Computer Science and Engineering',
                    'rajesh.staff@nexdemy.edu',
                    '+91 9876543200',
                    hash_password('Staff@2026'),
                    'faculty'
                ))
                conn.commit()

            # Seed Default 20 Students
            for stu in DEFAULT_20_STUDENTS:
                name, roll_no, dept, email, mobile, fee_status, avg_marks, att_attended, att_conducted = stu
                cur.execute("SELECT id FROM users WHERE roll_no = %s", (roll_no,))
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO users (name, roll_no, dept, email, mobile, password_hash, role)
                        VALUES (%s, %s, %s, %s, %s, %s, 'student')
                    """, (name, roll_no, dept, email, mobile, hash_password('Student@2026')))
                    conn.commit()
                    seed_default_courses_for_student(cur, roll_no, avg_marks, att_attended, att_conducted)
                    seed_default_fees_for_student(cur, roll_no, fee_status)
                    conn.commit()

        conn.close()
        print("[+] MySQL Database `nexdemy_db` initialized successfully!")
        return True
    except Exception as e:
        print(f"[!] MySQL initialization notice: {e}")
        return False

def seed_default_courses_for_student(cur, roll_no, base_marks=95, attended=42, conducted=45):
    t1 = max(10, min(25, int(base_marks * 0.25)))
    t2 = max(10, min(25, int(base_marks * 0.24)))
    model = max(20, min(50, int(base_marks * 0.48)))
    assign = max(5, min(10, int(base_marks * 0.10)))
    total = min(100, t1 + t2 + int(model * 0.8) + assign)

    if total >= 90: grade, gp = 'O', 10
    elif total >= 80: grade, gp = 'A+', 9
    elif total >= 70: grade, gp = 'A', 8
    elif total >= 60: grade, gp = 'B+', 7
    else: grade, gp = 'B', 6

    courses = [
        ('CS601', 'Computer Networks', 3, 'Dr. A. Rajesh', 'LH-201', t1, t2, model, assign, total, grade, gp, conducted, attended, '2026-05-04', 'FN (09:30 AM)'),
        ('CS602', 'Data Structures & Algorithms', 4, 'Prof. S. Priyadharshini', 'Lab 3', t1, t2, model, assign, total, grade, gp, conducted, attended, '2026-05-07', 'FN (09:30 AM)'),
        ('CS603', 'Distributed Computing', 3, 'Dr. M. Karthik', 'LH-203', max(10, t1-2), max(10, t2-1), max(20, model-3), assign, max(50, total-5), 'A+' if total >= 85 else grade, gp if total >= 85 else 9, conducted, max(25, attended-3), '2026-05-11', 'FN (09:30 AM)'),
        ('TA601', 'Tamil', 2, 'Prof. K. Selvam', 'LH-105', min(25, t1+1), min(25, t2+1), min(50, model+1), assign, min(100, total+3), 'O', 10, 30, max(20, int(attended * 0.65)), '2026-05-14', 'FN (09:30 AM)'),
        ('MA601', 'Matrices and Calculus', 4, 'Dr. V. Lakshmi', 'LH-201', max(10, t1-3), max(10, t2-2), max(20, model-4), assign, max(50, total-7), 'A+' if total >= 80 else grade, 9 if total >= 80 else 8, conducted, max(25, attended-2), '2026-05-18', 'FN (09:30 AM)'),
        ('HS601', 'Communication Period', 3, 'Prof. E. Catherine', 'Lang Lab', t1, t2, model, assign, total, grade, gp, 35, max(25, int(attended * 0.77)), '2026-05-22', 'AN (02:00 PM)')
    ]
    cur.executemany("""
        INSERT INTO student_marks 
        (roll_no, code, title, credits, faculty, venue, test1, test2, model, assign, total, grade, grade_point, conducted, attended, exam_date, session)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [(roll_no, *c) for c in courses])

def seed_default_fees_for_student(cur, roll_no, status='Paid'):
    is_paid = (status == 'Paid')
    fees = [
        ('Tuition Fee', 45000.00, '2026-01-10', status, 'TXN9842189032' if is_paid else 'UNPAID', '2026-01-08' if is_paid else '-'),
        ('Special Lab & Network Infra Fee', 8500.00, '2026-01-10', status, 'TXN9842189045' if is_paid else 'UNPAID', '2026-01-08' if is_paid else '-'),
        ('Semester End Exam & Hall Ticket Fee', 3200.00, '2026-03-15', status, 'TXN9842190112' if is_paid else 'UNPAID', '2026-03-12' if is_paid else '-'),
        ('Library & Digital Access Fee', 1500.00, '2026-01-10', status, 'TXN9842191560' if is_paid else 'UNPAID', '2026-01-08' if is_paid else '-')
    ]
    cur.executemany("""
        INSERT INTO fee_ledger (roll_no, fee_name, amount, due_date, status, txn_id, paid_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, [(roll_no, *f) for f in fees])

def authenticate_user(identifier, password, expected_role=None):
    try:
        conn = get_connection(use_db=True)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM users 
                WHERE (roll_no = %s OR email = %s)
            """, (identifier, identifier))
            user = cur.fetchone()

            if not user:
                conn.close()
                return {'success': False, 'message': 'Account not found in Nexdemy. Please click "Register" to create your account.'}

            if expected_role:
                if expected_role == 'faculty' and user['role'] != 'faculty':
                    conn.close()
                    return {
                        'success': False,
                        'message': 'Access Denied: Student accounts must sign in using the "Student Sign In" tab.'
                    }
                elif expected_role == 'student' and user['role'] != 'student':
                    conn.close()
                    return {
                        'success': False,
                        'message': 'Access Denied: Faculty accounts must sign in using the "Faculty Sign In" tab.'
                    }

            input_hash = hash_password(password)
            if user['password_hash'] != input_hash:
                conn.close()
                return {'success': False, 'message': 'Incorrect password. Access denied.'}

            cur.execute("SELECT * FROM student_marks WHERE roll_no = %s", (user['roll_no'],))
            courses = cur.fetchall()

            if not courses and user['role'] == 'student':
                seed_default_courses_for_student(cur, user['roll_no'])
                seed_default_fees_for_student(cur, user['roll_no'])
                conn.commit()
                cur.execute("SELECT * FROM student_marks WHERE roll_no = %s", (user['roll_no'],))
                courses = cur.fetchall()

            cur.execute("SELECT * FROM fee_ledger WHERE roll_no = %s", (user['roll_no'],))
            fees = cur.fetchall()

            conn.close()
            for f in fees:
                f['amount'] = float(f['amount'])
            user.pop('password_hash', None)
            return {
                'success': True,
                'user': user,
                'courses': courses,
                'fees': fees,
                'message': f"Welcome back, {user['name']}!"
            }
    except Exception as e:
        return {'success': False, 'message': f"Database error: {str(e)}"}

# ==========================================================================
# GMAIL SMTP OTP EMAIL ENGINE
# ==========================================================================
def send_otp_email(to_email, otp_code, user_name="Nexdemy User"):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Nexdemy Portal — Password Reset OTP: {otp_code}"
        msg['From'] = f"Nexdemy Security Center <{SMTP_USER}>"
        msg['To'] = to_email

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 24px; color: #0f172a; }}
            .email-container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 14px rgba(0,0,0,0.06); }}
            .header {{ background: #111317; color: #ffffff; padding: 24px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 22px; letter-spacing: 0.05em; }}
            .header p {{ margin: 4px 0 0 0; font-size: 12px; color: #94a3b8; }}
            .body {{ padding: 28px 24px; }}
            .otp-box {{ background: #f8fafc; border: 2px dashed #0284c7; border-radius: 8px; padding: 18px; text-align: center; margin: 24px 0; }}
            .otp-code {{ font-size: 36px; font-weight: 800; color: #0f172a; letter-spacing: 8px; font-family: monospace; }}
            .footer {{ background: #f8fafc; padding: 16px; text-align: center; font-size: 11px; color: #64748b; border-top: 1px solid #e2e8f0; }}
          </style>
        </head>
        <body>
          <div class="email-container">
            <div class="header">
              <h1>NEXDEMY</h1>
              <p>Smart Academic & Student Management Portal</p>
            </div>
            <div class="body">
              <h2 style="font-size: 18px; color: #0f172a; margin-top: 0;">Password Reset Request</h2>
              <p>Hello <strong>{user_name}</strong>,</p>
              <p>We received a request to reset your password for the Nexdemy Portal. Use the following 6-digit One-Time Password (OTP) to complete your verification:</p>
              
              <div class="otp-box">
                <div style="font-size: 12px; font-weight: bold; color: #0284c7; margin-bottom: 4px;">YOUR VERIFICATION CODE</div>
                <div class="otp-code">{otp_code}</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 6px;">Valid for 10 minutes only. Do not share this code.</div>
              </div>

              <p style="font-size: 13px; color: #475569;">If you did not initiate this request, please ignore this email or contact the Nexdemy Security Administrator immediately.</p>
            </div>
            <div class="footer">
              &copy; 2026 Nexdemy Academic Portal | Office of Controller of Examinations & Student Affairs<br>
              Karur - 639001, Tamil Nadu, India
            </div>
          </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_content, 'html'))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [to_email], msg.as_string())
        server.quit()

        print(f"[+] Successfully dispatched OTP email to: {to_email}")
        return True
    except Exception as e:
        print(f"[!] SMTP Dispatch Error: {e}")
        return False

def request_password_reset(identifier, override_email=None):
    try:
        target_email = None
        user_name = "Nexdemy User"
        roll_no = identifier

        conn = get_connection(use_db=True)
        with conn.cursor() as cur:
            cur.execute("SELECT name, roll_no, email FROM users WHERE roll_no = %s OR email = %s", (identifier, identifier))
            user = cur.fetchone()
            if user:
                user_name = user['name']
                roll_no = user['roll_no']
                target_email = user['email']
        conn.close()

        if override_email and '@' in override_email:
            target_email = override_email
        elif '@' in identifier:
            target_email = identifier

        if not target_email or not '@' in target_email:
            target_email = 'postmanmail21@gmail.com'

        otp_code = str(random.randint(100000, 999999))
        OTP_STORE[roll_no.lower()] = {
            'otp': otp_code,
            'email': target_email,
            'timestamp': time.time()
        }
        OTP_STORE[target_email.lower()] = {
            'otp': otp_code,
            'roll_no': roll_no,
            'timestamp': time.time()
        }

        email_sent = send_otp_email(target_email, otp_code, user_name)
        masked_email = target_email[0:2] + '***@' + target_email.split('@')[1] if '@' in target_email else target_email
        return {
            'success': True,
            'message': f"6-Digit OTP successfully sent to {masked_email}!",
            'email': target_email,
            'identifier': roll_no,
            'email_sent': email_sent
        }
    except Exception as e:
        return {'success': False, 'message': f"Error requesting OTP: {str(e)}"}

def verify_otp_and_reset_password(identifier, otp, new_password):
    key = identifier.lower().strip()
    stored = OTP_STORE.get(key)

    if not stored:
        return {'success': False, 'message': 'No active OTP request found for this account. Please request a new OTP.'}

    if time.time() - stored['timestamp'] > 600:
        OTP_STORE.pop(key, None)
        return {'success': False, 'message': 'OTP has expired (10 minutes limit). Please request a fresh OTP.'}

    if stored['otp'] != otp.strip():
        return {'success': False, 'message': 'Invalid OTP code. Please check your email and try again.'}

    try:
        new_hash = hash_password(new_password)
        conn = get_connection(use_db=True)
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users 
                SET password_hash = %s 
                WHERE roll_no = %s OR email = %s
            """, (new_hash, identifier, identifier))
            conn.commit()
        conn.close()

        OTP_STORE.pop(key, None)
        return {'success': True, 'message': 'Password updated successfully! You can now sign in with your new password.'}
    except Exception as e:
        return {'success': False, 'message': f"Database error updating password: {str(e)}"}

def add_new_student_by_faculty(name, roll_no, dept, email, mobile, fee_status='Paid', cgpa=8.5, attendance_pct=85.0):
    """Adds a new student by faculty with initialized marks and fees."""
    try:
        conn = get_connection(use_db=True)
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE roll_no = %s", (roll_no,))
            if cur.fetchone():
                conn.close()
                return {'success': False, 'message': f'Register Number {roll_no} already exists in Nexdemy.'}

            pwd_hash = hash_password('Student@2026')
            cur.execute("""
                INSERT INTO users (name, roll_no, dept, email, mobile, password_hash, role)
                VALUES (%s, %s, %s, %s, %s, %s, 'student')
            """, (name, roll_no, dept, email, mobile, pwd_hash))

            base_marks = int(cgpa * 9.5)
            attended = int((attendance_pct / 100.0) * 45)
            seed_default_courses_for_student(cur, roll_no, base_marks=base_marks, attended=attended, conducted=45)
            seed_default_fees_for_student(cur, roll_no, status=fee_status)
            conn.commit()

        conn.close()
        return {'success': True, 'message': f'Student {name} ({roll_no}) successfully added to class roster!'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def register_user(name, roll_no, dept, email, mobile, password):
    try:
        conn = get_connection(use_db=True)
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE roll_no = %s", (roll_no,))
            if cur.fetchone():
                conn.close()
                return {'success': False, 'message': 'Register Number already registered in Nexdemy. Please Sign In.'}

            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                conn.close()
                return {'success': False, 'message': 'Official Email already registered. Please Sign In.'}

            pwd_hash = hash_password(password)
            cur.execute("""
                INSERT INTO users (name, roll_no, dept, email, mobile, password_hash, role)
                VALUES (%s, %s, %s, %s, %s, %s, 'student')
            """, (name, roll_no, dept, email, mobile, pwd_hash))
            
            seed_default_courses_for_student(cur, roll_no)
            seed_default_fees_for_student(cur, roll_no, 'Paid')
            conn.commit()

            cur.execute("SELECT * FROM users WHERE roll_no = %s", (roll_no,))
            user = cur.fetchone()
            cur.execute("SELECT * FROM student_marks WHERE roll_no = %s", (roll_no,))
            courses = cur.fetchall()
            cur.execute("SELECT * FROM fee_ledger WHERE roll_no = %s", (roll_no,))
            fees = cur.fetchall()

            conn.close()
            for f in fees:
                f['amount'] = float(f['amount'])
            user.pop('password_hash', None)
            return {
                'success': True,
                'user': user,
                'courses': courses,
                'fees': fees,
                'message': 'Registration successful! Welcome to Nexdemy.'
            }
    except Exception as e:
        return {'success': False, 'message': f"Registration error: {str(e)}"}

def get_faculty_class_roster():
    try:
        conn = get_connection(use_db=True)
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, roll_no, dept, email, mobile FROM users WHERE role = 'student' ORDER BY roll_no ASC")
            students = cur.fetchall()

            roster = []
            for s in students:
                roll = s['roll_no']
                cur.execute("SELECT * FROM student_marks WHERE roll_no = %s", (roll,))
                courses = cur.fetchall()

                cur.execute("SELECT status FROM fee_ledger WHERE roll_no = %s LIMIT 1", (roll,))
                fee_row = cur.fetchone()
                fee_status = fee_row['status'] if fee_row else 'Pending'

                tot_conducted = sum(c['conducted'] for c in courses) or 1
                tot_attended = sum(c['attended'] for c in courses)
                att_pct = round((tot_attended / tot_conducted) * 100, 1)

                tot_credits = sum(c['credits'] for c in courses) or 1
                tot_pts = sum(c['credits'] * c['grade_point'] for c in courses)
                cgpa = round(tot_pts / tot_credits, 2)

                roster.append({
                    'name': s['name'],
                    'roll_no': s['roll_no'],
                    'dept': s['dept'],
                    'email': s['email'],
                    'mobile': s['mobile'],
                    'fee_status': fee_status,
                    'attendance_pct': att_pct,
                    'cgpa': cgpa,
                    'courses': courses
                })

            conn.close()
            return {'success': True, 'roster': roster}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def update_user_profile(roll_no, name, dept, email, mobile):
    try:
        conn = get_connection(use_db=True)
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users 
                SET name = %s, dept = %s, email = %s, mobile = %s
                WHERE roll_no = %s
            """, (name, dept, email, mobile, roll_no))
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'Profile updated in MySQL database.'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def save_student_evaluation(roll_no, updated_courses, fee_status=None):
    try:
        conn = get_connection(use_db=True)
        with conn.cursor() as cur:
            for c in updated_courses:
                cur.execute("""
                    UPDATE student_marks
                    SET test1 = %s, test2 = %s, model = %s, assign = %s, total = %s,
                        grade = %s, grade_point = %s, attended = %s
                    WHERE roll_no = %s AND code = %s
                """, (
                    c.get('test1', 0),
                    c.get('test2', 0),
                    c.get('model', 0),
                    c.get('assign', 0),
                    c.get('total', 0),
                    c.get('grade', 'O'),
                    c.get('gradePoint', 10),
                    c.get('attended', 0),
                    roll_no,
                    c.get('code')
                ))
            
            if fee_status:
                cur.execute("""
                    UPDATE fee_ledger
                    SET status = %s
                    WHERE roll_no = %s
                """, (fee_status, roll_no))

            conn.commit()
            conn.close()
            return {'success': True, 'message': 'Student marks & fee status updated in MySQL.'}
    except Exception as e:
        return {'success': False, 'message': str(e)}
