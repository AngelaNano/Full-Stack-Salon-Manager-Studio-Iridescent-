# ✦ Studio Iridescent — Salon Management Dashboard

A full-stack booking and client management system built for **Studio Iridescent LLC**, a premium salon studio. Features real-time scheduling, client management, inventory tracking, automated notifications, and integrated financial analytics.

---

## 🔗 Live Demo

| | Link |
|---|---|
| **Live Dashboard** | https://studio-iridescent.vercel.app |
| **API Health** | https://full-stack-salon-manager-studio.onrender.com/api/health |
| **GitHub** | https://github.com/AngelaNano/studio-iridescent |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, React Router, React Query, Recharts |
| **Backend** | Python 3.11, Flask, SQLAlchemy, PostgreSQL |
| **Finance** | Python scripts — scikit-learn forecasting, QuickBooks API |
| **Deployment** | Vercel (frontend) + Render (backend + PostgreSQL) |
| **Email** | SMTP (Gmail / any provider) |
| **Auth** | API key middleware |

---

## Features

### Booking & Scheduling
- Create, update, and cancel appointments with conflict detection
- Real-time slot availability checker
- Status management: Pending → Confirmed → Completed

### Client Management
- Full client CRUD with search
- Appointment history per client
- Notes for preferences, allergies, etc.

### Inventory Tracking
- Stock levels with low-stock alerts
- Restock workflow
- Category and supplier tracking

### Customer Notifications
- Automated email confirmation on booking
- 24-hour appointment reminders
- Bulk reminder send for next-day appointments

### Financial Dashboard
- Revenue, expenses, and net profit (weekly / monthly / yearly)
- Revenue breakdown by service category
- Transaction log

### Python Finance Scripts
- `revenue_forecast.py` — 90-day ML revenue forecast using linear regression
- `expense_tracker.py` — P&L reports, monthly cashflow, Excel export
- `quickbooks_sync.py` — Two-way sync with QuickBooks Online

---

## Project Structure
studio-iridescent/
├── backend/
│   ├── app.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/models.py
│   ├── routes/
│   │   ├── appointments.py
│   │   ├── clients.py
│   │   ├── inventory.py
│   │   ├── notifications.py
│   │   └── finance.py
│   └── middleware/auth.py
├── frontend/
│   ├── package.json
│   └── src/
│       ├── App.js
│       ├── index.css
│       ├── api/client.js
│       └── pages/
│           ├── Dashboard.js
│           ├── Appointments.js
│           ├── Clients.js
│           ├── Inventory.js
│           └── Finance.js
└── finance/
├── requirements.txt
└── scripts/
├── revenue_forecast.py
├── expense_tracker.py
└── quickbooks_sync.py

---

## Getting Started

### 1. Clone the Repo
```bash
git clone https://github.com/AngelaNano/studio-iridescent.git
cd studio-iridescent
```

### 2. Set Up PostgreSQL
```bash
createdb studio_iridescent
```

### 3. Set Up Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask db init
flask db migrate -m "initial"
flask db upgrade
python seed.py
python app.py
```

### 4. Set Up Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm start
```

---

## Built By

Developed for **Studio Iridescent LLC** — a premium salon studio in Cape Coral, FL.

- Full-stack booking and client management dashboard
- Flask + PostgreSQL backend middleware for appointment workflows
- QuickBooks integration with custom Python analytics scripts
- 40% boost in operational efficiency · 30% improvement in cash flow visibility
