# ✦ Studio Iridescent — Salon Management Dashboard

A full-stack booking and client management system built for **Studio Iridescent LLC**, a premium salon studio. Features real-time scheduling, client management, inventory tracking, automated notifications, and integrated financial analytics.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, React Router, React Query, Recharts |
| **Backend** | Python 3.11, Flask, SQLAlchemy, PostgreSQL |
| **Finance** | Python scripts — scikit-learn forecasting, QuickBooks API |
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
---

## Live Demo

🔗 **Live UI:** https://studio-iridescent.vercel.app  
⚙️ **API:** https://full-stack-salon-manager-studio.onrender.com/api/health  
📁 **GitHub:** https://github.com/AngelaNano/studio-iridescent
