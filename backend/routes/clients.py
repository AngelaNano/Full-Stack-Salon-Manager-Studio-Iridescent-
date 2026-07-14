from flask import Blueprint, request, jsonify
from models.models import db
from models.models import Client

clients_bp = Blueprint("clients", __name__)

@clients_bp.route("/", methods=["GET"])
def get_clients():
    search = request.args.get("search", "")
    query = Client.query
    if search:
        query = query.filter(
            (Client.first_name.ilike(f"%{search}%")) |
            (Client.last_name.ilike(f"%{search}%")) |
            (Client.email.ilike(f"%{search}%"))
        )
    clients = query.order_by(Client.last_name).all()
    return jsonify([c.to_dict() for c in clients])

@clients_bp.route("/<int:client_id>", methods=["GET"])
def get_client(client_id):
    client = Client.query.get_or_404(client_id)
    data = client.to_dict()
    data["appointments"] = [a.to_dict() for a in client.appointments]
    return jsonify(data)

@clients_bp.route("/", methods=["POST"])
def create_client():
    data = request.get_json()
    required = ["first_name", "last_name", "email"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    existing = Client.query.filter_by(email=data["email"]).first()
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    client = Client(
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        phone=data.get("phone"),
        notes=data.get("notes"),
    )
    db.session.add(client)
    db.session.commit()
    return jsonify(client.to_dict()), 201

@clients_bp.route("/<int:client_id>", methods=["PUT"])
def update_client(client_id):
    client = Client.query.get_or_404(client_id)
    data = request.get_json()
    for field in ["first_name", "last_name", "email", "phone", "notes"]:
        if field in data:
            setattr(client, field, data[field])
    db.session.commit()
    return jsonify(client.to_dict())

@clients_bp.route("/<int:client_id>", methods=["DELETE"])
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": "Client deleted"})