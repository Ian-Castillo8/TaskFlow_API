import pytest
from app import create_app
from app.models import db

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def auth_token(client):
    client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    return response.get_json()["token"]

def test_create_task(client, auth_token):
    response = client.post("/api/tasks", json={
        "title": "Test Task",
        "description": "This is a test task"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 201
    assert response.get_json()["title"] == "Test Task"

def test_get_tasks(client, auth_token):
    client.post("/api/tasks", json={
        "title": "Test Task"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    response = client.get("/api/tasks",
        headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert len(response.get_json()) == 1

def test_update_task(client, auth_token):
    create = client.post("/api/tasks", json={
        "title": "Old Title"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    task_id = create.get_json()["id"]
    response = client.put(f"/api/tasks/{task_id}", json={
        "title": "New Title",
        "is_completed": True
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200

def test_delete_task(client, auth_token):
    create = client.post("/api/tasks", json={
        "title": "Task to delete"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    task_id = create.get_json()["id"]
    response = client.delete(f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 204

def test_get_tasks_unauthenticated(client):
    response = client.get("/api/tasks")
    assert response.status_code == 401