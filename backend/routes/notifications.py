from flask import Blueprint, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from models.models import Appointment, Client

notifications_bp = Blueprint("notifications", __name__)

def send_email(to_email: str, subject: str, body: str):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_user or not smtp_pass:
        print(f"[MOCK EMAIL] To: {to_email} | Subject: {subject}")
        return {"sent": False, "reason": "SMTP not configured — email logged"}

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())

    return {"sent": True}

@notifications_bp.route("/appointment-confirmation/<int:appointment_id>", methods=["POST"])
def send_confirmation(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    client = appointment.client

    body = f"""
    <h2>Appointment Confirmed — Studio Iridescent</h2>
    <p>Hi {client.first_name},</p>
    <p>Your appointment is confirmed:</p>
    <ul>
        <li><strong>Service:</strong> {appointment.service.name}</li>
        <li><strong>Date:</strong> {appointment.scheduled_at.strftime('%B %d, %Y at %I:%M %p')}</li>
        <li><strong>Duration:</strong> {appointment.service.duration_minutes} minutes</li>
    </ul>
    <p>See you soon! 💜</p>
    <p>— Studio Iridescent</p>
    """

    result = send_email(
        to_email=client.email,
        subject="Your Appointment at Studio Iridescent ✨",
        body=body,
    )
    return jsonify(result)

@notifications_bp.route("/reminder/<int:appointment_id>", methods=["POST"])
def send_reminder(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    client = appointment.client

    body = f"""
    <h2>Appointment Reminder — Studio Iridescent</h2>
    <p>Hi {client.first_name}, just a reminder about your appointment tomorrow:</p>
    <ul>
        <li><strong>Service:</strong> {appointment.service.name}</li>
        <li><strong>Time:</strong> {appointment.scheduled_at.strftime('%I:%M %p')}</li>
    </ul>
    <p>Reply to this email to reschedule if needed.</p>
    """

    result = send_email(
        to_email=client.email,
        subject="Reminder: Appointment Tomorrow at Studio Iridescent",
        body=body,
    )
    return jsonify(result)

@notifications_bp.route("/bulk-reminder", methods=["POST"])
def bulk_reminder():
    from datetime import datetime, timedelta
    tomorrow = datetime.utcnow().date() + timedelta(days=1)

    appointments = Appointment.query.filter(
        db.func.date(Appointment.scheduled_at) == tomorrow
    ).all()

    results = []
    for appt in appointments:
        result = send_email(
            to_email=appt.client.email,
            subject="Reminder: Appointment Tomorrow at Studio Iridescent",
            body=f"<p>Hi {appt.client.first_name}, see you tomorrow at {appt.scheduled_at.strftime('%I:%M %p')}!</p>"
        )
        results.append({"appointment_id": appt.id, **result})

    return jsonify({"reminders_sent": len(results), "results": results})