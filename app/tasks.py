from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, Task
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/api/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    user_id = int(get_jwt_identity())
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "is_completed": t.is_completed,
        "created_at": t.created_at.isoformat(),
        "due_date": t.due_date.isoformat() if t.due_date else None
    } for t in tasks]), 200


@tasks_bp.route("/api/tasks/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "created_at": task.created_at.isoformat(),
        "due_date": task.due_date.isoformat() if task.due_date else None
    }), 200


@tasks_bp.route("/api/tasks", methods=["POST"])
@jwt_required()
def create_task():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    task = Task(
        title=data["title"],
        description=data.get("description"),
        due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
        user_id=user_id
    )

    db.session.add(task)
    db.session.commit()
    return jsonify({"id": task.id, "title": task.title}), 201


@tasks_bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()

    if "description" in data:
        task.description = data["description"]

    if "is_completed" in data:
        task.is_completed = data["is_completed"]

    if "due_date" in data:
        task.due_date = (
            datetime.fromisoformat(data["due_date"])
            if data["due_date"]
            else None
    )

    db.session.commit()
    return jsonify({"message": "Task updated"}), 200


@tasks_bp.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 204