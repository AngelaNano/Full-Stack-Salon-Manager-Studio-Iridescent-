from flask import Blueprint, request, jsonify
from models.models import db
from models.models import Transaction
from sqlalchemy import func
from datetime import datetime, timedelta

finance_bp = Blueprint("finance", __name__)

@finance_bp.route("/transactions", methods=["GET"])
def get_transactions():
    tx_type = request.args.get("type")
    query = Transaction.query
    if tx_type:
        query = query.filter(Transaction.type == tx_type)
    transactions = query.order_by(Transaction.transaction_date.desc()).limit(100).all()
    return jsonify([t.to_dict() for t in transactions])

@finance_bp.route("/transactions", methods=["POST"])
def create_transaction():
    data = request.get_json()
    tx = Transaction(
        appointment_id=data.get("appointment_id"),
        type=data["type"],
        category=data.get("category"),
        amount=data["amount"],
        description=data.get("description"),
        transaction_date=datetime.fromisoformat(data.get("transaction_date", datetime.utcnow().isoformat())),
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify(tx.to_dict()), 201

@finance_bp.route("/summary", methods=["GET"])
def financial_summary():
    period = request.args.get("period", "month")

    if period == "week":
        start = datetime.utcnow() - timedelta(days=7)
    elif period == "year":
        start = datetime.utcnow() - timedelta(days=365)
    else:
        start = datetime.utcnow() - timedelta(days=30)

    revenue = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.type == "revenue",
        Transaction.transaction_date >= start
    ).scalar() or 0

    expenses = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.type == "expense",
        Transaction.transaction_date >= start
    ).scalar() or 0

    return jsonify({
        "period": period,
        "revenue": float(revenue),
        "expenses": float(expenses),
        "net_profit": float(revenue - expenses),
        "profit_margin": round((float(revenue - expenses) / float(revenue) * 100), 2) if revenue > 0 else 0,
    })

@finance_bp.route("/revenue-by-category", methods=["GET"])
def revenue_by_category():
    results = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.type == "revenue"
    ).group_by(Transaction.category).all()

    return jsonify([{"category": r[0], "total": float(r[1])} for r in results])