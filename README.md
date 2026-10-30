# ⚡ StaffSync — Modern Human Resource Management System

A **complete, production-grade HRMS** with two deployment options:

| Option | Stack | Status |
|--------|-------|--------|
| **Streamlit App** | Python + SQLite + Plotly | ✅ **Ready to deploy on Streamlit Cloud** |
| **MERN Stack** | MongoDB + Express + React + Node | ✅ Full codebase included |

---

## 🚀 Quick Start — Streamlit (Recommended for Deployment)

### Prerequisites
- Python 3.9+
- pip

### 1. Install dependencies
```bash
cd staffsync
pip install -r requirements.txt
```

### 2. Run locally
```bash
streamlit run app.py
```

### 3. Open browser
```
http://localhost:8501
```

### Demo Credentials
| Role | Email | Password |
|------|-------|----------|
| 👑 HR Administrator | `admin@staffsync.io` | `Admin@123` |
| 👔 Manager | `manager@staffsync.io` | `Manager@123` |
| 💼 Employee | `employee@staffsync.io` | `Employee@123` |

> The database (`staffsync.db`) is auto-created with rich seed data on first run.

---

## ☁️ Deploy to Streamlit Cloud

1. Push this folder to a **GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path** to `app.py`
5. Click **Deploy** — done!

> **Note:** Streamlit Cloud uses ephemeral storage. The SQLite DB resets on restart. For persistence, swap the SQLite backend with a cloud database (PostgreSQL via psycopg2 or MongoDB via pymongo) and update `database.py`.

---

## 🏗️ Features Implemented

### Authentication & Authorization
- ✅ Secure password hashing (PBKDF2-SHA256)
- ✅ Session-based auth via `st.session_state`
- ✅ Role-based access control (HR Admin / Manager / Employee)
- ✅ Registration with auto employee profile creation
- ✅ Password change with current-password verification
- ✅ Audit logging for all critical actions

### HR Administrator Dashboard
- ✅ Real-time KPI metrics (Total, Present, Pending Leaves, Trainings)
- ✅ Weekly attendance bar chart (Plotly)
- ✅ Department distribution donut chart (Plotly)
- ✅ Recent announcements & audit log
- ✅ Quick action buttons (Add Employee, Review Leaves, Post Announcement, Export)

### Employee Management
- ✅ Full employee directory with search, department & status filters
- ✅ Card grid view and interactive sortable table
- ✅ Add new employee (auto-generates code + user login)
- ✅ Edit designation, department, status, salary, phone
- ✅ Detailed profile with leave balances & attendance history
- ✅ Deactivate employee (disables login access)
- ✅ CSV export

### Leave Management
- ✅ Apply for leave (Casual / Sick / Earned / Unpaid)
- ✅ Date validation & overlap detection
- ✅ Leave balance adequacy check before submission
- ✅ Manager/HR approval with decision comments
- ✅ Balance auto-deducted on approval
- ✅ Cancel pending requests
- ✅ Organization-wide leave audit (HR)
- ✅ Leave policy reference table
- ✅ CSV export

### Attendance Tracking
- ✅ One-click Clock In / Clock Out
- ✅ Late detection (after 09:30 AM)
- ✅ Automatic shift duration calculation
- ✅ Personal attendance history (last 30 days)
- ✅ Manager team roster with today's status
- ✅ HR org-wide attendance view with date/dept filters
- ✅ Correction tool with mandatory audit reason
- ✅ CSV export

### Announcements
- ✅ HR creates/edits/deletes announcements
- ✅ Category tags (Company News / HR Policy / Urgent Alert / etc.)
- ✅ High priority flag with visual highlight
- ✅ Publish/Unpublish toggle
- ✅ Keyword search + category filter
- ✅ Auto-notification to all users on publish

### Training & Development
- ✅ Create training programs (title, trainer, dates, mode, capacity)
- ✅ Multi-employee enrollment with duplicate check
- ✅ Employee progress slider (0–100%)
- ✅ Status tracking (Enrolled / In Progress / Completed)
- ✅ Training catalog view for all employees
- ✅ My enrolled programs tab with progress bars
- ✅ Enrollment notifications

### Reports & Analytics
- ✅ Workforce KPI summary
- ✅ Avg compensation per department (bar)
- ✅ Department distribution (pie)
- ✅ Leave type breakdown by status (histogram)
- ✅ Attendance status distribution (pie)
- ✅ Master employee roster CSV export
- ✅ Full leave audit trail CSV export

### Notifications
- ✅ In-app notification center (bell dropdown)
- ✅ Unread count indicator
- ✅ Mark all as read
- ✅ Triggered on: leave submit, leave decision, announcements, training enrollment

### Profile & Settings
- ✅ Personal employment details view
- ✅ Contact info update (phone, address, emergency contact)
- ✅ Password change (with current password verification)
- ✅ Account activity log (audit trail)

---

## 🗄️ Database Schema (SQLite)

| Table | Purpose |
|-------|---------|
| `users` | Login credentials, roles, active status |
| `employees` | Full workforce profile with manager relationships |
| `leave_requests` | Leave applications, decisions, audit trail |
| `leave_balances` | Per-employee leave balance tracking |
| `attendance` | Daily punch records with correction support |
| `announcements` | Company broadcasts with category & priority |
| `training_programs` | Program catalog |
| `training_enrollments` | Employee enrollment & progress |
| `notifications` | In-app notification inbox |
| `audit_logs` | Security & action audit trail |

---

## 🛠️ MERN Stack (Full REST API + React Client)

The `mern_codebase/` folder contains a complete production-ready MERN implementation.

### Server Setup
```bash
cd mern_codebase/server
cp .env.example .env     # Fill in MONGO_URI and JWT_SECRET
npm install
node seed.js             # Seed demo data
npm run dev              # Starts on http://localhost:5000
```

### Client Setup
```bash
cd mern_codebase/client
npm install
npm run dev              # Starts on http://localhost:5173
```

### Run Both Concurrently
```bash
cd mern_codebase
npm install
npm run dev
```

### Server `.env` Variables
```
PORT=5000
MONGO_URI=mongodb://localhost:27017/staffsync
JWT_SECRET=replace_with_a_secure_random_secret_min_32_chars
JWT_EXPIRES_IN=7d
CLIENT_URL=http://localhost:5173
```

### API Endpoints
| Method | Endpoint | Auth | Role |
|--------|----------|------|------|
| POST | `/api/auth/login` | ❌ | All |
| GET | `/api/auth/me` | ✅ | All |
| PUT | `/api/auth/change-password` | ✅ | All |
| GET | `/api/employees` | ✅ | All |
| POST | `/api/employees` | ✅ | HR Admin |
| PUT | `/api/employees/:id` | ✅ | HR Admin |
| GET | `/api/leaves` | ✅ | All |
| POST | `/api/leaves` | ✅ | All |
| PUT | `/api/leaves/:id/review` | ✅ | Manager / HR |
| POST | `/api/attendance/punch` | ✅ | All |
| GET | `/api/attendance` | ✅ | All |
| PUT | `/api/attendance/:id/correct` | ✅ | HR Admin |
| GET | `/api/announcements` | ✅ | All |
| POST | `/api/announcements` | ✅ | HR Admin |
| DELETE | `/api/announcements/:id` | ✅ | HR Admin |
| GET | `/api/training` | ✅ | All |
| POST | `/api/training` | ✅ | Manager / HR |
| POST | `/api/training/:id/enroll` | ✅ | Manager / HR |
| GET | `/api/reports/dashboard-stats` | ✅ | All |

---

## 📁 Project Structure

```
staffsync/                         ← Streamlit App (deploy this)
├── app.py                         ← Main entry point
├── database.py                    ← SQLite schema + seed data
├── auth.py                        ← Auth, registration, sessions
├── ui_components.py               ← CSS, metric cards, navbar
├── pages_module/
│   ├── dashboard.py               ← HR / Manager / Employee dashboards
│   ├── employees.py               ← Employee directory & management
│   ├── leaves.py                  ← Leave application & approval
│   ├── attendance.py              ← Punch clock & corrections
│   ├── announcements.py           ← Broadcasts & news
│   ├── training.py                ← Programs & enrollments
│   ├── reports.py                 ← Analytics & CSV exports
│   └── profile.py                 ← Profile & password settings
├── .streamlit/config.toml         ← Theme configuration
├── requirements.txt               ← Python dependencies
└── staffsync.db                   ← Auto-created SQLite database

mern_codebase/                     ← Full MERN Stack
├── server/
│   ├── models/                    ← Mongoose models (7 schemas)
│   ├── routes/                    ← Express REST API routes
│   ├── middleware/                ← JWT auth + role authorization
│   ├── config/db.js               ← MongoDB connection
│   ├── seed.js                    ← Database seeder
│   └── server.js                  ← Express app entry point
└── client/
    └── src/
        ├── App.jsx                ← React Router setup
        ├── context/               ← Auth + Toast contexts
        ├── layouts/AppLayout.jsx  ← Sidebar + topbar
        ├── components/            ← DataTable, Modal, Badge, etc.
        ├── pages/                 ← All 9 page components
        ├── services/              ← Axios API service layer
        ├── hooks/useFetch.js      ← Generic data-fetching hook
        └── utils/helpers.js       ← Formatters, CSV download
```

---

## 🔐 Security Features
- Passwords hashed with PBKDF2-SHA256 (100,000 iterations)
- Role-based route protection (server-side, not just frontend)
- Session tokens stored only in `st.session_state`
- JWT with configurable expiry for MERN API
- Rate limiting on login endpoints (MERN)
- Mandatory reason for all administrative corrections
- Full audit log trail for sensitive operations

---

## 👥 Demo Team

| Name | Role | Email | Password |
|------|------|-------|----------|
| Eleanor Vance | HR Administrator | admin@staffsync.io | Admin@123 |
| Marcus Sterling | Manager (Engineering VP) | manager@staffsync.io | Manager@123 |
| Sophia Patel | Employee (Senior Engineer) | employee@staffsync.io | Employee@123 |
| David Kim | Employee (Frontend Eng) | david.kim@staffsync.io | Staff@123 |
| Jessica Taylor | Manager (Head of Growth) | jessica.t@staffsync.io | Staff@123 |
| Carlos Rodriguez | Employee (Finance Analyst) | carlos.r@staffsync.io | Staff@123 |
| Emily Chen | Employee (UI/UX Designer) | emily.c@staffsync.io | Staff@123 |
| Tariq Mansoor | Employee (HR Generalist) | tariq.m@staffsync.io | Staff@123 |

---

## 🐛 Troubleshooting

**Streamlit won't start?**
```bash
pip install streamlit plotly pandas
streamlit run app.py
```

**Database is empty / corrupted?**
```bash
del staffsync.db     # Windows
streamlit run app.py  # Will re-seed automatically
```

**MERN — MongoDB connection refused?**
- Ensure MongoDB is running: `mongod --dbpath ./data`
- Or use MongoDB Atlas — paste the connection string into `.env`

**MERN — JWT errors?**
- Make sure `JWT_SECRET` in `.env` is set and at least 32 characters

---

*Built with ❤️ for portfolio, college projects, and internship demonstrations.*
