from app import create_app
from models.models import db
from models.models import Client, Service, Appointment, InventoryItem, Transaction, AppointmentStatus
from datetime import datetime, timedelta
import random

app = create_app()

SERVICES = [
    {"name": "Haircut & Style", "description": "Precision cut and blowout finish", "duration_minutes": 60, "price": 85},
    {"name": "Color Treatment", "description": "Single-process color with toner", "duration_minutes": 120, "price": 180},
    {"name": "Blowout", "description": "Shampoo, condition, and blowdry", "duration_minutes": 45, "price": 55},
    {"name": "Deep Conditioning", "description": "Intensive moisture treatment", "duration_minutes": 45, "price": 65},
    {"name": "Balayage", "description": "Hand-painted highlight technique", "duration_minutes": 180, "price": 280},
    {"name": "Keratin Treatment", "description": "Smoothing protein treatment", "duration_minutes": 150, "price": 220},
]

CLIENTS = [
    {"first_name": "Naomi", "last_name": "Chen", "email": "client1@studio.internal", "phone": ""},
    {"first_name": "Sofia", "last_name": "Reyes", "email": "client2@studio.internal", "phone": ""},
    {"first_name": "Aaliyah", "last_name": "Washington", "email": "client3@studio.internal", "phone": ""},
    {"first_name": "Priya", "last_name": "Sharma", "email": "client4@studio.internal", "phone": ""},
    {"first_name": "Zoe", "last_name": "Kim", "email": "client5@studio.internal", "phone": ""},
    {"first_name": "Isabelle", "last_name": "Martin", "email": "client6@studio.internal", "phone": ""},
    {"first_name": "Maya", "last_name": "Thompson", "email": "client7@studio.internal", "phone": ""},
    {"first_name": "Aria", "last_name": "Patel", "email": "client8@studio.internal", "phone": ""},
]

INVENTORY = [
    {"name": "Wella Color Charm 6N", "category": "Color", "quantity": 12, "reorder_threshold": 5, "unit_cost": 8.99, "supplier": "Wella Professional"},
    {"name": "Olaplex No. 3 Hair Perfector", "category": "Treatment", "quantity": 3, "reorder_threshold": 5, "unit_cost": 28.00, "supplier": "Olaplex"},
    {"name": "Kenra Platinum Silkening Mist", "category": "Styling", "quantity": 8, "reorder_threshold": 4, "unit_cost": 24.50, "supplier": "Kenra"},
    {"name": "Redken All Soft Shampoo (L)", "category": "Shampoo", "quantity": 2, "reorder_threshold": 4, "unit_cost": 19.00, "supplier": "Redken"},
    {"name": "Foil Sheets 500ct", "category": "Supplies", "quantity": 1, "reorder_threshold": 2, "unit_cost": 14.00, "supplier": "Beauty Supply Co"},
    {"name": "Latex-free Gloves (Box)", "category": "Supplies", "quantity": 7, "reorder_threshold": 3, "unit_cost": 12.00, "supplier": "Beauty Supply Co"},
    {"name": "Brazilian Bond Builder B3", "category": "Treatment", "quantity": 5, "reorder_threshold": 3, "unit_cost": 32.00, "supplier": "B3 Pro"},
    {"name": "Moroccanoil Treatment (Large)", "category": "Styling", "quantity": 4, "reorder_threshold": 3, "unit_cost": 44.00, "supplier": "Moroccanoil"},
]

EXPENSE_CATEGORIES = ["Supplies", "Utilities", "Rent", "Marketing", "Insurance", "Equipment"]

def seed():
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        db.create_all()

        print("Seeding services...")
        services = [Service(**s) for s in SERVICES]
        db.session.add_all(services)
        db.session.flush()

        print("Seeding clients...")
        clients = [Client(**c) for c in CLIENTS]
        db.session.add_all(clients)
        db.session.flush()

        print("Seeding inventory...")
        items = [InventoryItem(**i) for i in INVENTORY]
        db.session.add_all(items)
        db.session.flush()

        print("Seeding appointments and transactions (60 days)...")
        statuses = [AppointmentStatus.CONFIRMED, AppointmentStatus.COMPLETED, AppointmentStatus.COMPLETED, AppointmentStatus.COMPLETED]

        for days_ago in range(60, -1, -1):
            appt_date = datetime.utcnow() - timedelta(days=days_ago)
            num_appts = random.randint(2, 5)

            for i in range(num_appts):
                client = random.choice(clients)
                service = random.choice(services)
                hour = random.choice([9, 10, 11, 13, 14, 15, 16, 17])
                scheduled = appt_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                status = random.choice(statuses) if days_ago > 0 else AppointmentStatus.CONFIRMED

                appt = Appointment(
                    client_id=client.id,
                    service_id=service.id,
                    scheduled_at=scheduled,
                    status=status,
                    created_at=appt_date,
                )
                db.session.add(appt)
                db.session.flush()

                if status == AppointmentStatus.COMPLETED:
                    tx = Transaction(
                        appointment_id=appt.id,
                        type="revenue",
                        category=service.name,
                        amount=float(service.price),
                        description=f"{service.name} — {client.first_name} {client.last_name}",
                        transaction_date=scheduled,
                    )
                    db.session.add(tx)

            if days_ago % 7 == 0:
                expense = Transaction(
                    type="expense",
                    category=random.choice(EXPENSE_CATEGORIES),
                    amount=round(random.uniform(50, 400), 2),
                    description="Operating expense",
                    transaction_date=appt_date,
                )
                db.session.add(expense)

        db.session.commit()
        print("✦ Database seeded successfully!")
        print(f"  {len(clients)} clients")
        print(f"  {len(services)} services")
        print(f"  {len(items)} inventory items")

if __name__ == "__main__":
    seed()