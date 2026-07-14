from flask import Blueprint, request, jsonify
from models.models import db
from models.models import InventoryItem
from datetime import datetime

inventory_bp = Blueprint("inventory", __name__)

@inventory_bp.route("/", methods=["GET"])
def get_inventory():
    low_stock_only = request.args.get("low_stock") == "true"
    query = InventoryItem.query
    if low_stock_only:
        query = query.filter(InventoryItem.quantity <= InventoryItem.reorder_threshold)
    items = query.order_by(InventoryItem.name).all()
    return jsonify([i.to_dict() for i in items])

@inventory_bp.route("/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    return jsonify(item.to_dict())

@inventory_bp.route("/", methods=["POST"])
def create_item():
    data = request.get_json()
    item = InventoryItem(
        name=data["name"],
        category=data.get("category"),
        quantity=data.get("quantity", 0),
        reorder_threshold=data.get("reorder_threshold", 5),
        unit_cost=data.get("unit_cost"),
        supplier=data.get("supplier"),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@inventory_bp.route("/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    data = request.get_json()
    for field in ["name", "category", "quantity", "reorder_threshold", "unit_cost", "supplier"]:
        if field in data:
            setattr(item, field, data[field])
    if "quantity" in data:
        item.last_restocked = datetime.utcnow()
    db.session.commit()
    return jsonify(item.to_dict())

@inventory_bp.route("/alerts", methods=["GET"])
def low_stock_alerts():
    items = InventoryItem.query.filter(
        InventoryItem.quantity <= InventoryItem.reorder_threshold
    ).all()
    return jsonify({
        "count": len(items),
        "items": [i.to_dict() for i in items]
    })