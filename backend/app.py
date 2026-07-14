from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:3000"])

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@localhost:5432/studio_iridescent"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    db.init_app(app)
    migrate.init_app(app, db)

    from routes.appointments import appointments_bp
    from routes.clients import clients_bp
    from routes.inventory import inventory_bp
    from routes.notifications import notifications_bp
    from routes.finance import finance_bp

    app.register_blueprint(appointments_bp, url_prefix="/api/appointments")
    app.register_blueprint(clients_bp, url_prefix="/api/clients")
    app.register_blueprint(inventory_bp, url_prefix="/api/inventory")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
    app.register_blueprint(finance_bp, url_prefix="/api/finance")

    @app.route("/api/health")
    def health():
        return {"status": "ok", "message": "Studio Iridescent API running"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)