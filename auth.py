"""
StaffSync - Authentication & Authorization Layer
Handles user login, session management, password hashing, role checks, and quick demo switching.
"""

import streamlit as st
import datetime
from database import (
    execute_single, 
    execute_query, 
    verify_password, 
    hash_password,
    get_connection
)

def authenticate_user(email: str, password: str):
    """Authenticate user with email and password."""
    query = """
    SELECT u.id, u.email, u.password_hash, u.role, u.is_active, u.employee_id,
           e.first_name, e.last_name, e.department, e.designation, e.avatar_url, e.employee_code, e.manager_id
    FROM users u
    LEFT JOIN employees e ON u.employee_id = e.id
    WHERE LOWER(u.email) = LOWER(?)
    """
    row = execute_single(query, (email.strip(),))
    if not row:
        return None, "Invalid email or user not found."
    
    if not row["is_active"]:
        return None, "This account has been deactivated. Please contact HR."

    if not verify_password(password, row["password_hash"]):
        return None, "Incorrect password. Please try again."

    user = dict(row)
    del user["password_hash"]
    return user, None

def login_user(user: dict):
    """Set user in Streamlit session state."""
    st.session_state["authenticated"] = True
    st.session_state["user"] = user
    # Log audit entry
    try:
        execute_query(
            "INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)",
            (user["id"], "User Login", f"User {user['email']} successfully logged in as {user['role']}."),
            commit=True
        )
    except Exception:
        pass

def logout_user():
    """Clear session and log out."""
    if "user" in st.session_state and st.session_state["user"]:
        try:
            execute_query(
                "INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)",
                (st.session_state["user"]["id"], "User Logout", f"User {st.session_state['user']['email']} logged out."),
                commit=True
            )
        except Exception:
            pass
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.session_state["current_page"] = "Dashboard"

def get_current_user():
    """Get the currently logged-in user or None."""
    if st.session_state.get("authenticated", False):
        return st.session_state.get("user")
    return None

def is_hr():
    user = get_current_user()
    return user is not None and user.get("role") == "HR Administrator"

def is_manager():
    user = get_current_user()
    return user is not None and user.get("role") in ("Manager", "HR Administrator")

def is_employee():
    user = get_current_user()
    return user is not None

def quick_demo_login(role: str):
    """Fast-track login for demonstration purposes."""
    role_email_map = {
        "HR Administrator": "admin@staffsync.io",
        "Manager": "manager@staffsync.io",
        "Employee": "employee@staffsync.io"
    }
    target_email = role_email_map.get(role)
    if target_email:
        query = """
        SELECT u.id, u.email, u.role, u.is_active, u.employee_id,
               e.first_name, e.last_name, e.department, e.designation, e.avatar_url, e.employee_code, e.manager_id
        FROM users u
        LEFT JOIN employees e ON u.employee_id = e.id
        WHERE u.email = ?
        """
        row = execute_single(query, (target_email,))
        if row:
            login_user(dict(row))
            st.rerun()

def register_user(first_name, last_name, email, password, role, department, designation, phone=""):
    """Register a new user and associate an employee profile."""
    # Check if email exists
    existing = execute_single("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
    if existing:
        return False, "An account with this email already exists."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Determine employee code
        cursor.execute("SELECT MAX(id) FROM employees")
        last_id = cursor.fetchone()[0] or 1000
        new_code = f"EMP-{last_id + 1}"
        today_str = datetime.date.today().strftime('%Y-%m-%d')

        # Insert Employee
        cursor.execute("""
        INSERT INTO employees (
            employee_code, first_name, last_name, email, phone, 
            department, designation, joining_date, employment_status, salary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Full-time', 75000)
        """, (new_code, first_name.strip(), last_name.strip(), email.strip().lower(), phone.strip(), department, designation, today_str))
        
        emp_id = cursor.lastrowid

        # Insert User
        pwd_hash = hash_password(password)
        cursor.execute("""
        INSERT INTO users (email, password_hash, role, employee_id)
        VALUES (?, ?, ?, ?)
        """, (email.strip().lower(), pwd_hash, role, emp_id))
        user_id = cursor.lastrowid

        # Insert Default Leave Balance
        cursor.execute("""
        INSERT INTO leave_balances (employee_id, casual_total, casual_used, sick_total, sick_used, earned_total, earned_used, unpaid_used)
        VALUES (?, 12, 0, 10, 0, 15, 0, 0)
        """, (emp_id,))

        # Notification
        cursor.execute("""
        INSERT INTO notifications (user_id, title, message, type)
        VALUES (?, 'Welcome to StaffSync', 'Your account has been successfully set up with role ' || ?, 'system')
        """, (user_id, role))

        # Audit Log
        cursor.execute("""
        INSERT INTO audit_logs (user_id, action, details)
        VALUES (?, 'User Registration', 'Registered new user ' || ? || ' with role ' || ?)
        """, (user_id, email, role))

        conn.commit()
        return True, "Registration successful! You can now log in."
    except Exception as e:
        conn.rollback()
        return False, f"Registration failed: {str(e)}"
    finally:
        conn.close()

def change_password(user_id: int, current_pwd: str, new_pwd: str):
    """Update user password securely."""
    row = execute_single("SELECT password_hash FROM users WHERE id = ?", (user_id,))
    if not row or not verify_password(current_pwd, row["password_hash"]):
        return False, "Current password is incorrect."
    
    if len(new_pwd) < 6:
        return False, "New password must be at least 6 characters long."

    new_hash = hash_password(new_pwd)
    execute_query("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id), commit=True)
    execute_query(
        "INSERT INTO audit_logs (user_id, action, details) VALUES (?, 'Password Change', 'User changed their password.')",
        (user_id,), commit=True
    )
    return True, "Password updated successfully!"
