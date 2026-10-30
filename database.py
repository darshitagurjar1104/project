"""
StaffSync - Database Engine & Initializer
Uses SQLite for zero-config, portable deployment on Streamlit Cloud and local environments.
Provides full relational schemas, helper accessors, and pre-seeded enterprise HR data.
"""

import sqlite3
import hashlib
import os
import datetime
from pathlib import Path

DB_FILE = Path(__file__).parent / "staffsync.db"

def get_connection():
    """Return an active connection with Row factory enabled."""
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password: str, salt: str = "staffsync_secure_salt_2026") -> str:
    """Hash passwords using PBKDF2 with SHA256."""
    return hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    ).hex()

def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify input password against stored hash."""
    return hash_password(plain_password) == password_hash

def init_db():
    """Create all required tables and populate seed data if not present."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('HR Administrator', 'Manager', 'Employee')),
        employee_id INTEGER,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL
    )
    """)

    # 2. Employees Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_code TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        avatar_url TEXT,
        department TEXT NOT NULL,
        designation TEXT NOT NULL,
        joining_date TEXT NOT NULL,
        employment_status TEXT DEFAULT 'Full-time' CHECK(employment_status IN ('Full-time', 'Part-time', 'Contract', 'Probation', 'Inactive')),
        manager_id INTEGER,
        address TEXT,
        emergency_contact_name TEXT,
        emergency_contact_phone TEXT,
        salary REAL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (manager_id) REFERENCES employees(id) ON DELETE SET NULL
    )
    """)

    # 3. Leave Requests Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        leave_type TEXT NOT NULL CHECK(leave_type IN ('Casual Leave', 'Sick Leave', 'Earned Leave', 'Unpaid Leave')),
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        total_days REAL NOT NULL,
        reason TEXT NOT NULL,
        status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Approved', 'Rejected', 'Cancelled')),
        reviewed_by INTEGER,
        decision_comment TEXT,
        applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
        FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
    )
    """)

    # 4. Leave Balances Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_balances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER UNIQUE NOT NULL,
        casual_total REAL DEFAULT 12,
        casual_used REAL DEFAULT 0,
        sick_total REAL DEFAULT 10,
        sick_used REAL DEFAULT 0,
        earned_total REAL DEFAULT 15,
        earned_used REAL DEFAULT 0,
        unpaid_used REAL DEFAULT 0,
        year INTEGER DEFAULT 2026,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
    )
    """)

    # 5. Attendance Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        check_in TEXT,
        check_out TEXT,
        total_hours REAL DEFAULT 0,
        status TEXT DEFAULT 'Present' CHECK(status IN ('Present', 'Late', 'Half-day', 'Absent', 'On Leave')),
        is_corrected INTEGER DEFAULT 0,
        correction_reason TEXT,
        corrected_by INTEGER,
        UNIQUE(employee_id, date),
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
        FOREIGN KEY (corrected_by) REFERENCES users(id) ON DELETE SET NULL
    )
    """)

    # 6. Announcements Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT NOT NULL CHECK(category IN ('Company News', 'HR Policy', 'Urgent Alert', 'Events & Social', 'Tech & Engineering')),
        is_important INTEGER DEFAULT 0,
        is_published INTEGER DEFAULT 1,
        created_by INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # 7. Training Programs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS training_programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        trainer TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        mode TEXT DEFAULT 'Online' CHECK(mode IN ('Online', 'In-Person', 'Hybrid')),
        location TEXT,
        capacity INTEGER DEFAULT 30,
        status TEXT DEFAULT 'Upcoming' CHECK(status IN ('Upcoming', 'In Progress', 'Completed')),
        created_by INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # 8. Training Enrollments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS training_enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        training_id INTEGER NOT NULL,
        employee_id INTEGER NOT NULL,
        progress INTEGER DEFAULT 0 CHECK(progress >= 0 AND progress <= 100),
        status TEXT DEFAULT 'Enrolled' CHECK(status IN ('Enrolled', 'In Progress', 'Completed')),
        enrolled_at TEXT DEFAULT CURRENT_TIMESTAMP,
        completed_at TEXT,
        UNIQUE(training_id, employee_id),
        FOREIGN KEY (training_id) REFERENCES training_programs(id) ON DELETE CASCADE,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
    )
    """)

    # 9. Notifications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT DEFAULT 'system' CHECK(type IN ('leave', 'announcement', 'training', 'system', 'attendance')),
        is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # 10. Audit Log Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT,
        ip_address TEXT DEFAULT '127.0.0.1',
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    )
    """)

    conn.commit()

    # Check if seed data exists
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        seed_database(conn)

    conn.close()

def seed_database(conn):
    """Seed comprehensive initial dataset."""
    cursor = conn.cursor()
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    two_days_ago = (datetime.date.today() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
    three_days_ago = (datetime.date.today() - datetime.timedelta(days=3)).strftime('%Y-%m-%d')

    # Seed Employees
    employees = [
        # 1. Eleanor Vance - HR Director
        ("EMP-1001", "Eleanor", "Vance", "admin@staffsync.io", "+1 (555) 234-5678", 
         "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150", 
         "Human Resources", "Chief People Officer", "2021-03-15", "Full-time", None, 
         "742 Evergreen Terrace, San Francisco, CA", "Arthur Vance", "+1 (555) 998-1122", 145000),
        
        # 2. Marcus Sterling - Engineering Manager
        ("EMP-1002", "Marcus", "Sterling", "manager@staffsync.io", "+1 (555) 345-6789", 
         "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150", 
         "Engineering", "VP of Engineering", "2021-06-01", "Full-time", 1, 
         "10880 Wilshire Blvd, Los Angeles, CA", "Clara Sterling", "+1 (555) 887-3344", 160000),
        
        # 3. Sophia Patel - Senior Full Stack Engineer (assigned to Marcus)
        ("EMP-1003", "Sophia", "Patel", "employee@staffsync.io", "+1 (555) 456-7890", 
         "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150", 
         "Engineering", "Senior Full-Stack Engineer", "2022-01-10", "Full-time", 2, 
         "500 Howard Street, San Francisco, CA", "Raj Patel", "+1 (555) 776-5566", 125000),

        # 4. David Kim - Frontend Developer (assigned to Marcus)
        ("EMP-1004", "David", "Kim", "david.kim@staffsync.io", "+1 (555) 567-8901", 
         "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150", 
         "Engineering", "Frontend Engineer", "2023-04-18", "Full-time", 2, 
         "220 Montgomery St, San Francisco, CA", "Mina Kim", "+1 (555) 665-7788", 98000),

        # 5. Jessica Taylor - Marketing Lead
        ("EMP-1005", "Jessica", "Taylor", "jessica.t@staffsync.io", "+1 (555) 678-9012", 
         "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150", 
         "Marketing", "Head of Growth", "2022-08-01", "Full-time", 1, 
         "450 Mission St, San Francisco, CA", "Tom Taylor", "+1 (555) 554-9900", 115000),

        # 6. Carlos Rodriguez - Financial Analyst
        ("EMP-1006", "Carlos", "Rodriguez", "carlos.r@staffsync.io", "+1 (555) 789-0123", 
         "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150", 
         "Finance", "Lead Financial Analyst", "2022-11-15", "Full-time", 1, 
         "101 California St, San Francisco, CA", "Elena Rodriguez", "+1 (555) 443-1122", 110000),

        # 7. Emily Chen - Product Designer (assigned to Marcus)
        ("EMP-1007", "Emily", "Chen", "emily.c@staffsync.io", "+1 (555) 890-1234", 
         "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150", 
         "Design", "Lead UI/UX Designer", "2023-02-01", "Full-time", 2, 
         "345 Spear St, San Francisco, CA", "Kevin Chen", "+1 (555) 332-2233", 105000),

        # 8. Tariq Mansoor - HR Specialist (assigned to Eleanor)
        ("EMP-1008", "Tariq", "Mansoor", "tariq.m@staffsync.io", "+1 (555) 901-2345", 
         "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150", 
         "Human Resources", "HR Generalist & Talent Ops", "2023-07-01", "Full-time", 1, 
         "55 2nd St, San Francisco, CA", "Zainab Mansoor", "+1 (555) 221-3344", 82000),
    ]

    cursor.executemany("""
    INSERT INTO employees (
        employee_code, first_name, last_name, email, phone, avatar_url, 
        department, designation, joining_date, employment_status, manager_id, 
        address, emergency_contact_name, emergency_contact_phone, salary
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, employees)

    # Seed Users for Authentication
    # Passwords:
    # admin@staffsync.io -> Admin@123
    # manager@staffsync.io -> Manager@123
    # employee@staffsync.io -> Employee@123
    # Others -> Staff@123
    users = [
        ("admin@staffsync.io", hash_password("Admin@123"), "HR Administrator", 1),
        ("manager@staffsync.io", hash_password("Manager@123"), "Manager", 2),
        ("employee@staffsync.io", hash_password("Employee@123"), "Employee", 3),
        ("david.kim@staffsync.io", hash_password("Staff@123"), "Employee", 4),
        ("jessica.t@staffsync.io", hash_password("Staff@123"), "Manager", 5),
        ("carlos.r@staffsync.io", hash_password("Staff@123"), "Employee", 6),
        ("emily.c@staffsync.io", hash_password("Staff@123"), "Employee", 7),
        ("tariq.m@staffsync.io", hash_password("Staff@123"), "Employee", 8),
    ]

    cursor.executemany("""
    INSERT INTO users (email, password_hash, role, employee_id)
    VALUES (?, ?, ?, ?)
    """, users)

    # Seed Leave Balances for all 8 employees
    for emp_id in range(1, 9):
        cursor.execute("""
        INSERT INTO leave_balances (employee_id, casual_total, casual_used, sick_total, sick_used, earned_total, earned_used, unpaid_used)
        VALUES (?, 12, 2, 10, 1, 15, 3, 0)
        """, (emp_id,))

    # Seed Leave Requests
    leave_requests = [
        (3, "Casual Leave", today_str, today_str, 1, "Personal family gathering and celebration", "Pending", None, None),
        (4, "Sick Leave", yesterday_str, yesterday_str, 1, "Viral fever and physician recommended rest", "Approved", 2, "Get well soon David, approved."),
        (7, "Earned Leave", "2026-11-15", "2026-11-18", 4, "Annual family travel vacation", "Pending", None, None),
        (6, "Casual Leave", three_days_ago, two_days_ago, 2, "Home renovation and inspection", "Approved", 1, "Approved as requested."),
        (3, "Sick Leave", "2026-09-10", "2026-09-11", 2, "Migraine recovery", "Approved", 2, "Approved, take care."),
    ]
    cursor.executemany("""
    INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, total_days, reason, status, reviewed_by, decision_comment)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, leave_requests)

    # Seed Attendance for Today and past days
    attendance_records = [
        # Today
        (1, today_str, "08:45:00", None, 0, "Present", 0, None, None),
        (2, today_str, "08:55:00", None, 0, "Present", 0, None, None),
        (3, today_str, "09:05:00", None, 0, "Present", 0, None, None),
        (4, today_str, "09:40:00", None, 0, "Late", 0, None, None),
        (5, today_str, "08:30:00", None, 0, "Present", 0, None, None),
        (6, today_str, "09:00:00", None, 0, "Present", 0, None, None),
        (7, today_str, None, None, 0, "Absent", 0, None, None),
        (8, today_str, "08:50:00", None, 0, "Present", 0, None, None),

        # Yesterday
        (1, yesterday_str, "08:50:00", "17:30:00", 8.67, "Present", 0, None, None),
        (2, yesterday_str, "09:00:00", "17:45:00", 8.75, "Present", 0, None, None),
        (3, yesterday_str, "08:55:00", "18:00:00", 9.08, "Present", 0, None, None),
        (4, yesterday_str, None, None, 0, "On Leave", 0, None, None),
        (5, yesterday_str, "08:40:00", "17:15:00", 8.58, "Present", 0, None, None),
        (6, yesterday_str, "09:10:00", "17:40:00", 8.50, "Present", 0, None, None),
        (7, yesterday_str, "09:00:00", "17:30:00", 8.50, "Present", 0, None, None),
        (8, yesterday_str, "08:45:00", "17:00:00", 8.25, "Present", 0, None, None),

        # Two days ago
        (1, two_days_ago, "08:40:00", "17:20:00", 8.67, "Present", 0, None, None),
        (2, two_days_ago, "08:50:00", "17:30:00", 8.67, "Present", 0, None, None),
        (3, two_days_ago, "09:00:00", "17:50:00", 8.83, "Present", 0, None, None),
        (4, two_days_ago, "09:15:00", "17:45:00", 8.50, "Present", 0, None, None),
        (5, two_days_ago, "08:35:00", "17:00:00", 8.42, "Present", 0, None, None),
        (6, two_days_ago, None, None, 0, "On Leave", 0, None, None),
        (7, two_days_ago, "08:55:00", "17:30:00", 8.58, "Present", 0, None, None),
        (8, two_days_ago, "09:00:00", "17:15:00", 8.25, "Present", 0, None, None),
    ]

    cursor.executemany("""
    INSERT INTO attendance (
        employee_id, date, check_in, check_out, total_hours, 
        status, is_corrected, correction_reason, corrected_by
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, attendance_records)

    # Seed Announcements
    announcements = [
        ("Annual Health & Wellness Benefit Rollout 2026", 
         "We are thrilled to announce our upgraded comprehensive health insurance coverage and gym reimbursement starting next month. Please review the updated policy portal for provider details.",
         "HR Policy", 1, 1, 1),
        ("Q4 Town Hall & Innovation Showcase", 
         "Join us this Thursday at 3:00 PM EST for our quarterly company-wide Town Hall. We will be celebrating top performers and previewing our 2027 product roadmap.",
         "Company News", 1, 1, 1),
        ("Mandatory Annual Cybersecurity & Data Privacy Training", 
         "All employees are required to complete the ISO 27001 compliance training module before November 20th. Progress will be tracked via the training portal.",
         "Urgent Alert", 1, 1, 1),
        ("StaffSync Hackathon: AI Workflows for Modern Enterprise", 
         "Registration is now open for our 48-hour engineering hackathon! Exciting prizes and mentorship opportunities await.",
         "Tech & Engineering", 0, 1, 2),
    ]

    cursor.executemany("""
    INSERT INTO announcements (title, content, category, is_important, is_published, created_by)
    VALUES (?, ?, ?, ?, ?, ?)
    """, announcements)

    # Seed Training Programs
    training_programs = [
        ("Enterprise Microservices Architecture with Docker & K8s", 
         "Hands-on workshop mastering cloud native patterns, Kubernetes orchestration, and resilient microservices.",
         "Dr. Aris Thorne", "2026-11-05", "2026-11-12", "Online", "Virtual Zoom Classroom", 25, "Upcoming", 2),
        ("Managerial Leadership & High-Performance Team Coaching", 
         "Executive development program covering 1-on-1 coaching, conflict resolution, OKR goal setting, and strategic alignment.",
         "Eleanor Vance & Forbes Coaches", "2026-10-20", "2026-11-02", "Hybrid", "Executive Boardroom & Online", 15, "In Progress", 1),
        ("Modern UX Research & Design Systems Mastery", 
         "Deep dive into user interviewing methodologies, design token architecture, and Figma auto-layout best practices.",
         "Sarah Lindqvist", "2026-10-01", "2026-10-15", "Online", "Design Guild Portal", 20, "Completed", 1),
        ("Cybersecurity & Zero Trust Security Architecture", 
         "Mandatory corporate security baseline focusing on phishing prevention, credential hygiene, and incident reporting.",
         "SecOps Global", "2026-11-01", "2026-11-20", "Online", "LMS Portal", 100, "Upcoming", 1),
    ]

    cursor.executemany("""
    INSERT INTO training_programs (title, description, trainer, start_date, end_date, mode, location, capacity, status, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, training_programs)

    # Seed Training Enrollments
    enrollments = [
        (1, 3, 40, "In Progress"),   # Sophia in Microservices
        (1, 4, 25, "In Progress"),   # David in Microservices
        (2, 2, 75, "In Progress"),   # Marcus in Managerial Leadership
        (2, 5, 60, "In Progress"),   # Jessica in Managerial Leadership
        (3, 7, 100, "Completed"),    # Emily in UX Research
        (3, 3, 100, "Completed"),    # Sophia in UX Research
        (4, 3, 0, "Enrolled"),       # Sophia in CyberSec
        (4, 4, 0, "Enrolled"),       # David in CyberSec
    ]

    cursor.executemany("""
    INSERT INTO training_enrollments (training_id, employee_id, progress, status)
    VALUES (?, ?, ?, ?)
    """, enrollments)

    # Seed Notifications
    notifications = [
        (3, "Leave Request Submitted", "Your Casual Leave request for today has been submitted for manager review.", "leave", 0),
        (2, "New Team Leave Request", "Sophia Patel submitted a leave request for today awaiting your review.", "leave", 0),
        (3, "Training Enrolled", "You have been enrolled in 'Enterprise Microservices Architecture'.", "training", 1),
        (1, "HR Analytics Alert", "Monthly attendance reports for October are ready for review.", "system", 0),
        (2, "Training Reminder", "Managerial Leadership session starts this Thursday at 2 PM.", "training", 0),
    ]

    cursor.executemany("""
    INSERT INTO notifications (user_id, title, message, type, is_read)
    VALUES (?, ?, ?, ?, ?)
    """, notifications)

    # Seed Audit Log
    audit_logs = [
        (1, "System Initialization", "StaffSync platform initialized with baseline company profile.", "127.0.0.1"),
        (1, "Policy Published", "Published Annual Health & Wellness Benefit Rollout 2026.", "127.0.0.1"),
        (2, "Leave Approval", "Approved leave request for David Kim (EMP-1004).", "127.0.0.1"),
        (3, "Attendance Clock-In", "Sophia Patel clocked in at 09:05:00.", "127.0.0.1"),
    ]

    cursor.executemany("""
    INSERT INTO audit_logs (user_id, action, details, ip_address)
    VALUES (?, ?, ?, ?)
    """, audit_logs)

    conn.commit()

# Helper queries
def execute_query(query: str, params=(), commit=False):
    """Safely execute query and return results or lastrowid."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if commit:
            conn.commit()
            result = cursor.lastrowid
        else:
            result = cursor.fetchall()
        return result
    finally:
        conn.close()

def execute_single(query: str, params=()):
    """Execute query and fetch a single record."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        return cursor.fetchone()
    finally:
        conn.close()
