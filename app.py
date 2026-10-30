"""
StaffSync — Modern Human Resource Management System
Main Streamlit Application Entrypoint
Provides role-based dashboards, authentication, navigation, and module routing.
"""

import streamlit as st
import datetime

# Configure page metadata first
st.set_page_config(
    page_title="StaffSync — Modern HR Management System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from database import init_db, get_connection
from auth import (
    authenticate_user, 
    login_user, 
    logout_user, 
    get_current_user, 
    register_user, 
    quick_demo_login,
    is_hr,
    is_manager
)
from ui_components import inject_custom_css, render_top_navbar
from pages_module.dashboard import render_dashboard
from pages_module.employees import render_employees
from pages_module.leaves import render_leaves
from pages_module.attendance import render_attendance
from pages_module.announcements import render_announcements
from pages_module.training import render_training
from pages_module.reports import render_reports
from pages_module.profile import render_profile

# Initialize database schemas and seed data
init_db()

# Apply SaaS custom design CSS
inject_custom_css()

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"

def render_login_page():
    """Render the branded login and registration screen."""
    col_left, col_right = st.columns([1.1, 1], gap="large")

    with col_left:
        st.markdown("""
        <div style="padding: 30px 20px 20px 10px;">
            <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 24px;">
                <div style="background: linear-gradient(135deg, #2563EB, #1D4ED8); width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 26px; color: white;">⚡</div>
                <div>
                    <h1 style="margin: 0; font-size: 32px; font-weight: 800; color: #0F172A; letter-spacing: -0.5px;">StaffSync</h1>
                    <div style="color: #64748B; font-size: 15px; font-weight: 500;">Next-Gen Human Resource Management Platform</div>
                </div>
            </div>
            <p style="font-size: 16px; color: #334155; line-height: 1.6; margin-bottom: 24px;">
                Streamline organizational talent, simplify leave approvals, track daily attendance, and gain real-time workforce intelligence with an enterprise-ready HRMS.
            </p>
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 14px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 20px;">
                <h4 style="margin-top: 0; color: #1E293B; font-size: 15px;">🌟 Core Capabilities:</h4>
                <ul style="color: #475569; font-size: 14px; line-height: 1.8; margin-bottom: 0; padding-left: 20px;">
                    <li><strong>Role-Based Access:</strong> Tailored portals for HR Admin, Manager, and Employee.</li>
                    <li><strong>Leave Governance:</strong> Automated balance tracking, date validations, & manager approvals.</li>
                    <li><strong>Precision Attendance:</strong> One-click punch in/out with shift duration metrics.</li>
                    <li><strong>Corporate Learning:</strong> Skill development catalogs & employee progress tracking.</li>
                    <li><strong>Workforce Analytics:</strong> Interactive Plotly headcount & payroll insights.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Quick 1-Click Demo Login Panel for Evaluators
        st.markdown("##### 🚀 Fast Demo Switcher (Instant 1-Click Access):")
        d1, d2, d3 = st.columns(3)
        with d1:
            if st.button("👑 HR Admin", use_container_width=True, help="Login as Eleanor Vance (Chief People Officer)"):
                quick_demo_login("HR Administrator")
        with d2:
            if st.button("👔 Manager", use_container_width=True, help="Login as Marcus Sterling (VP of Engineering)"):
                quick_demo_login("Manager")
        with d3:
            if st.button("💼 Employee", use_container_width=True, help="Login as Sophia Patel (Senior Engineer)"):
                quick_demo_login("Employee")

    with col_right:
        st.markdown("<br><br>", unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with tab_login:
            st.markdown("#### Access StaffSync Portal")
            st.caption("Enter your organizational credentials to continue.")

            with st.form("form_login"):
                email = st.text_input("Work Email", placeholder="e.g. admin@staffsync.io")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                remember = st.checkbox("Remember this session", value=True)

                login_btn = st.form_submit_button("Sign In to Portal", type="primary", use_container_width=True)

                if login_btn:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
                        user, err = authenticate_user(email, password)
                        if err:
                            st.error(err)
                        else:
                            login_user(user)
                            st.rerun()

            st.caption("Demo Default Accounts:")
            st.caption("• HR Admin: `admin@staffsync.io` / `Admin@123`")
            st.caption("• Manager: `manager@staffsync.io` / `Manager@123`")
            st.caption("• Employee: `employee@staffsync.io` / `Employee@123`")

        with tab_register:
            st.markdown("#### Employee Registration")
            st.caption("Join your company's StaffSync workspace.")

            with st.form("form_register"):
                rc1, rc2 = st.columns(2)
                with rc1:
                    r_fn = st.text_input("First Name *")
                    r_email = st.text_input("Work Email *")
                    r_dept = st.selectbox("Department *", ["Engineering", "Human Resources", "Marketing", "Finance", "Design"])
                with rc2:
                    r_ln = st.text_input("Last Name *")
                    r_pwd = st.text_input("Password *", type="password")
                    r_role = st.selectbox("Access Role *", ["Employee", "Manager", "HR Administrator"])

                r_desig = st.text_input("Job Designation *", placeholder="e.g. Associate Software Engineer")
                r_phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")

                reg_btn = st.form_submit_button("Complete Registration", type="primary", use_container_width=True)

                if reg_btn:
                    if not r_fn or not r_ln or not r_email or not r_pwd or not r_desig:
                        st.error("Please complete all required fields marked with *.")
                    elif len(r_pwd) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        ok, msg = register_user(r_fn, r_ln, r_email, r_pwd, r_role, r_dept, r_desig, r_phone)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

def render_sidebar(user: dict):
    """Render role-specific sidebar navigation."""
    role = user.get("role", "Employee")
    emp_code = user.get("employee_code", "EMP-0000")
    first_name = user.get("first_name", "User")
    last_name = user.get("last_name", "")
    avatar = user.get("avatar_url") or "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100"

    with st.sidebar:
        # Brand Logo in Sidebar
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; padding: 10px 0 20px 0;">
            <div style="background: #2563EB; width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; color: white;">⚡</div>
            <div>
                <div style="font-weight: 800; font-size: 20px; color: white; letter-spacing: -0.3px;">StaffSync</div>
                <div style="font-size: 11px; color: #94A3B8;">HR Management System</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Profile Card
        st.markdown(f"""
        <div style="background: #1E293B; border-radius: 10px; padding: 12px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
            <img src="{avatar}" style="width: 38px; height: 38px; border-radius: 50%; object-fit: cover; border: 1px solid #3B82F6;" />
            <div style="overflow: hidden;">
                <div style="font-weight: 700; font-size: 13px; color: white; white-space: nowrap; text-overflow: ellipsis;">{first_name} {last_name}</div>
                <div style="font-size: 11px; color: #60A5FA;">{role}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation Options based on Role
        if role == "HR Administrator":
            nav_options = [
                "Dashboard", 
                "Employees", 
                "Leave Management", 
                "Attendance", 
                "Announcements", 
                "Training Programs", 
                "Reports & Analytics", 
                "Profile & Settings"
            ]
        elif role == "Manager":
            nav_options = [
                "Dashboard", 
                "Employees", 
                "Leave Management", 
                "Attendance", 
                "Announcements", 
                "Training Programs", 
                "Profile & Settings"
            ]
        else: # Employee
            nav_options = [
                "Dashboard", 
                "Employees", 
                "Leave Management", 
                "Attendance", 
                "Announcements", 
                "Training Programs", 
                "Profile & Settings"
            ]

        # Ensure current_page is valid
        if st.session_state["current_page"] not in nav_options:
            st.session_state["current_page"] = "Dashboard"

        selected = st.radio(
            "Navigation Menu",
            nav_options,
            index=nav_options.index(st.session_state["current_page"]),
            label_visibility="collapsed"
        )
        st.session_state["current_page"] = selected

        st.markdown("---")

        # Quick Role Switcher for demo
        st.caption("Switch Role Perspective:")
        col_sw1, col_sw2, col_sw3 = st.columns(3)
        with col_sw1:
            if st.button("👑 HR", help="Eleanor Vance (HR Admin)", key="sb_hr"):
                quick_demo_login("HR Administrator")
        with col_sw2:
            if st.button("👔 Mgr", help="Marcus Sterling (Manager)", key="sb_mgr"):
                quick_demo_login("Manager")
        with col_sw3:
            if st.button("💼 Emp", help="Sophia Patel (Employee)", key="sb_emp"):
                quick_demo_login("Employee")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚪 Sign Out", use_container_width=True):
            logout_user()
            st.rerun()

def main():
    if not st.session_state.get("authenticated", False):
        render_login_page()
    else:
        user = st.session_state["user"]
        render_top_navbar(user)
        render_sidebar(user)

        # Route page
        current = st.session_state["current_page"]

        if current == "Dashboard":
            render_dashboard(user)
        elif current == "Employees":
            render_employees(user)
        elif current == "Leave Management":
            render_leaves(user)
        elif current == "Attendance":
            render_attendance(user)
        elif current == "Announcements":
            render_announcements(user)
        elif current == "Training Programs":
            render_training(user)
        elif current == "Reports & Analytics":
            render_reports(user)
        elif current == "Profile & Settings":
            render_profile(user)

if __name__ == "__main__":
    main()
