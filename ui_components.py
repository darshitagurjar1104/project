"""
StaffSync - Modern UI/UX Component Library & Theme Styling
Provides custom CSS, branded badges, metric cards, navigation headers, and notification center.
"""

import streamlit as st
import datetime
from database import execute_query

def inject_custom_css():
    """Inject modern, SaaS-grade CSS into the Streamlit application."""
    css = """
    <style>
        /* Import Google Inter font */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #0F172A;
        }

        /* App container background */
        .stApp {
            background-color: #F8FAFC;
        }

        /* Top Header Styling */
        .staffsync-header {
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            border-radius: 16px;
            padding: 24px 28px;
            color: white;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.12), 0 8px 10px -6px rgba(15, 23, 42, 0.08);
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .staffsync-brand {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .staffsync-logo-icon {
            background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
            width: 44px;
            height: 44px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            font-weight: 800;
            color: white;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
        }

        /* Metric Card Styling */
        .metric-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 20px;
            box-shadow: 0 2px 8px -2px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease-in-out;
            margin-bottom: 12px;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.07);
            border-color: #CBD5E1;
        }
        .metric-title {
            font-size: 13px;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }
        .metric-value {
            font-size: 30px;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.1;
        }
        .metric-subtitle {
            font-size: 12px;
            color: #94A3B8;
            margin-top: 6px;
        }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.2px;
            text-align: center;
        }
        .badge-present { background-color: #DCFCE7; color: #15803D; }
        .badge-absent { background-color: #FEE2E2; color: #B91C1C; }
        .badge-late { background-color: #FEF3C7; color: #B45309; }
        .badge-pending { background-color: #FEF9C3; color: #A16207; }
        .badge-approved { background-color: #DCFCE7; color: #15803D; }
        .badge-rejected { background-color: #FEE2E2; color: #B91C1C; }
        .badge-urgent { background-color: #FEE2E2; color: #DC2626; border: 1px solid #FECACA; }
        .badge-info { background-color: #DBEAFE; color: #1D4ED8; }
        .badge-role { background-color: #EFF6FF; color: #2563EB; border: 1px solid #BFDBFE; }

        /* Announcement Card */
        .announcement-card {
            background: #FFFFFF;
            border-radius: 14px;
            border: 1px solid #E2E8F0;
            padding: 22px;
            margin-bottom: 16px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            border-left: 5px solid #2563EB;
        }
        .announcement-card.important {
            border-left: 5px solid #EF4444;
            background: #FEF2F2;
        }

        /* Section Container */
        .content-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 24px;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #0F172A;
            border-right: 1px solid #1E293B;
        }
        section[data-testid="stSidebar"] * {
            color: #F8FAFC !important;
        }
        section[data-testid="stSidebar"] hr {
            border-color: #334155 !important;
        }

        /* Buttons custom polish */
        div.stButton > button:first-child {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            border-bottom: 2px solid #E2E8F0;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 18px;
            border-radius: 8px 8px 0 0;
            font-weight: 600;
            color: #64748B;
        }
        .stTabs [aria-selected="true"] {
            color: #2563EB !important;
            border-bottom: 3px solid #2563EB;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_metric_card(title: str, value: str, subtitle: str = "", icon: str = "📊", bg_color: str = "#FFFFFF"):
    """Render a premium responsive dashboard KPI card."""
    html = f"""
    <div class="metric-card" style="background: {bg_color};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
                {f'<div class="metric-subtitle">{subtitle}</div>' if subtitle else ''}
            </div>
            <div style="font-size: 24px; background: #F1F5F9; width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                {icon}
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_badge(text: str, badge_type: str = "info"):
    """Render a colored status badge."""
    return f'<span class="badge badge-{badge_type}">{text}</span>'

def render_top_navbar(user: dict):
    """Render professional top branding navbar and user quick-info."""
    first_name = user.get("first_name") or "User"
    last_name = user.get("last_name") or ""
    role = user.get("role", "Employee")
    dept = user.get("department", "Organization")
    emp_code = user.get("employee_code", "EMP-0000")
    avatar_url = user.get("avatar_url") or "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100"

    # Notification count
    unread_count_row = execute_query(
        "SELECT COUNT(*) as cnt FROM notifications WHERE user_id = ? AND is_read = 0",
        (user["id"],)
    )
    unread_count = unread_count_row[0]["cnt"] if unread_count_row else 0

    st.markdown(f"""
    <div class="staffsync-header">
        <div class="staffsync-brand">
            <div class="staffsync-logo-icon">⚡</div>
            <div>
                <div style="font-size: 22px; font-weight: 800; letter-spacing: -0.5px; color: #FFFFFF;">
                    StaffSync
                    <span style="font-size: 11px; background: #2563EB; padding: 2px 8px; border-radius: 12px; margin-left: 8px; font-weight: 600; text-transform: uppercase;">HRMS Enterprise</span>
                </div>
                <div style="font-size: 13px; color: #94A3B8; margin-top: 2px;">
                    Modern Human Resource Management Platform
                </div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="text-align: right;">
                <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">
                    {first_name} {last_name}
                </div>
                <div style="font-size: 12px; color: #93C5FD;">
                    {role} • {dept} ({emp_code})
                </div>
            </div>
            <img src="{avatar_url}" style="width: 44px; height: 44px; border-radius: 50%; border: 2px solid #3B82F6; object-fit: cover;" />
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_notification_drawer(user_id: int):
    """Notification accordion viewer with mark-all-read capability."""
    notifications = execute_query(
        "SELECT id, title, message, type, is_read, created_at FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
        (user_id,)
    )
    unread = sum(1 for n in notifications if not n["is_read"])
    
    with st.expander(f"🔔 Notifications Center ({unread} unread)", expanded=False):
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.caption("Real-time updates regarding leave approvals, announcements, and trainings.")
        with col_b:
            if unread > 0:
                if st.button("Mark all as read", key="btn_mark_all_read", use_container_width=True):
                    execute_query("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,), commit=True)
                    st.toast("All notifications marked as read.")
                    st.rerun()

        if not notifications:
            st.info("No notifications at this time.")
        else:
            for notif in notifications:
                status_dot = "🔵" if not notif["is_read"] else "⚪"
                st.markdown(f"""
                <div style="padding: 10px 14px; background: {'#F0FDF4' if not notif['is_read'] else '#F8FAFC'}; border: 1px solid {'#BBF7D0' if not notif['is_read'] else '#E2E8F0'}; border-radius: 8px; margin-bottom: 8px;">
                    <div style="font-weight: 600; font-size: 13px; color: #1E293B;">{status_dot} {notif['title']}</div>
                    <div style="font-size: 12px; color: #475569; margin-top: 2px;">{notif['message']}</div>
                    <div style="font-size: 10px; color: #94A3B8; margin-top: 4px;">{notif['created_at']}</div>
                </div>
                """, unsafe_allow_html=True)
