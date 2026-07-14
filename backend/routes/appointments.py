from flask import Blueprint, request, jsonify
from models.models import db
from models.models import Appointment, Client, Service, AppointmentStatus
from datetime import datetime
from middleware.auth import require_auth

appointments_bp = Blueprint("appointments", __name__)

@appointments_bp.route("/", methods=["GET"])
def get_appointments():
    status = request.args.get("status")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    query = Appointment.query

    if status:
        query = query.filter(Appointment.status == AppointmentStatus(status))
    if date_from:
        query = query.filter(Appointment.scheduled_at >= datetime.fromisoformat(date_from))
    if date_to:
        query = query.filter(Appointment.scheduled_at <= datetime.fromisoformat(date_to))

    appointments = query.order_by(Appointment.scheduled_at.asc()).all()
    return jsonify([a.to_dict() for a in appointments])

@appointments_bp.route("/<int:appointment_id>", methods=["GET"])
def get_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    return jsonify(appointment.to_dict())

@appointments_bp.route("/", methods=["POST"])
def create_appointment():
    data = request.get_json()

    required = ["client_id", "service_id", "scheduled_at"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    scheduled_at = datetime.fromisoformat(data["scheduled_at"])
    service = Service.query.get_or_404(data["service_id"])

    conflict = Appointment.query.filter(
        Appointment.scheduled_at == scheduled_at,
        Appointment.status != AppointmentStatus.CANCELLED
    ).first()

    if conflict:
        return jsonify({"error": "Time slot already booked"}), 409

    appointment = Appointment(
        client_id=data["client_id"],
        service_id=data["service_id"],
        scheduled_at=scheduled_at,
        notes=data.get("notes"),
        status=AppointmentStatus.CONFIRMED,
    )
    db.session.add(appointment)
    db.session.commit()

    return jsonify(appointment.to_dict()), 201

@appointments_bp.route("/<int:appointment_id>", methods=["PATCH"])
def update_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    data = request.get_json()

    if "status" in data:
        appointment.status = AppointmentStatus(data["status"])
    if "notes" in data:
        appointment.notes = data["notes"]
    if "scheduled_at" in data:
        appointment.scheduled_at = datetime.fromisoformat(data["scheduled_at"])

    db.session.commit()
    return jsonify(appointment.to_dict())

@appointments_bp.route("/<int:appointment_id>", methods=["DELETE"])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = AppointmentStatus.CANCELLED
    db.session.commit()
    return jsonify({"message": "Appointment cancelled"})

@appointments_bp.route("/availability", methods=["GET"])
def get_availability():
    date_str = request.args.get("date")
    if not date_str:
        return jsonify({"error": "date parameter required"}), 400

    from datetime import timedelta
    target_date = datetime.fromisoformat(date_str)

    slots = []
    for hour in range(9, 19):
        slot_time = target_date.replace(hour=hour, minute=0, second=0)
        booked = Appointment.query.filter(
            Appointment.scheduled_at == slot_time,
            Appointment.status != AppointmentStatus.CANCELLED
        ).first()
        slots.append({
            "time": slot_time.isoformat(),
            "available": booked is None
        })

    return jsonify(slots)