from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class AppointmentStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Client(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    appointments = db.relationship("Appointment", back_populates="client", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "appointment_count": len(self.appointments),
        }

class Service(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "duration_minutes": self.duration_minutes,
            "price": float(self.price),
            "active": self.active,
        }

class Appointment(db.Model):
    __tablename__ = "appointments"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.relationship("Client", back_populates="appointments")
    service = db.relationship("Service")

    def to_dict(self):
        return {
            "id": self.id,
            "client": self.client.to_dict(),
            "service": self.service.to_dict(),
            "scheduled_at": self.scheduled_at.isoformat(),
            "status": self.status.value,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }

class InventoryItem(db.Model):
    __tablename__ = "inventory"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80))
    quantity = db.Column(db.Integer, default=0)
    reorder_threshold = db.Column(db.Integer, default=5)
    unit_cost = db.Column(db.Numeric(10, 2))
    supplier = db.Column(db.String(120))
    last_restocked = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "reorder_threshold": self.reorder_threshold,
            "unit_cost": float(self.unit_cost) if self.unit_cost else None,
            "supplier": self.supplier,
            "low_stock": self.quantity <= self.reorder_threshold,
            "last_restocked": self.last_restocked.isoformat() if self.last_restocked else None,
        }

class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=True)
    type = db.Column(db.String(20))
    category = db.Column(db.String(80))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "type": self.type,
            "category": self.category,
            "amount": float(self.amount),
            "description": self.description,
            "transaction_date": self.transaction_date.isoformat(),
        }
