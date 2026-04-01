from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from bcrypt import hashpw, gensalt, checkpw
from .models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Username, email, or password are required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 400

    password_hash = hashpw(data["password"].encode("utf-8"), gensalt()).decode("utf-8")

    user = User(
        username=data["username"],
        email=data["email"],
        password_hash=password_hash
    )

    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "username": user.username}), 201

@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not checkpw(data["password"].encode("utf-8"), user.password_hash.encode("utf-8")):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "username": user.username}), 200