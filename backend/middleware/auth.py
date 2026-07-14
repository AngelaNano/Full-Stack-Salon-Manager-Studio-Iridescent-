from functools import wraps
from flask import request, jsonify
import os

API_KEY = os.getenv("API_KEY", "dev-api-key-change-in-production")

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if not key or key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated