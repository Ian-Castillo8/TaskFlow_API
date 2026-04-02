from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from .models import db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    jwt = JWTManager(app)

    from .auth import auth_bp
    from .tasks import tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    # Swagger UI
    swaggerui_blueprint = get_swaggerui_blueprint(
        "/docs",
        "/static/swagger.json",
        config={"app_name": "TaskFlow API"}
    )
    app.register_blueprint(swaggerui_blueprint)

    with app.app_context():
        db.create_all()

    return app