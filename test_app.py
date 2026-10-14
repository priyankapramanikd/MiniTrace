
import pytest

import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Use a temporary database so tests do not change project data.
    test_db = tmp_path / "test_minitrace.db"
    monkeypatch.setattr(app_module, "DB_FILE", test_db)

    app_module.init_db()

    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_stats_endpoint(client):
    response = client.get("/api/stats")

    assert response.status_code == 200
    assert response.json["total"] == 0
    assert response.json["summary"]["INFO"] == 0


def test_create_log(client):
    response = client.post(
        "/api/logs",
        json={
            "level": "ERROR",
            "message": "Payment service failed",
            "source": "payment-service"
        }
    )

    assert response.status_code == 201
    assert response.json["log"]["level"] == "ERROR"
    assert response.json["log"]["message"] == "Payment service failed"


def test_created_log_can_be_retrieved(client):
    client.post(
        "/api/logs",
        json={
            "level": "INFO",
            "message": "Service started",
            "source": "test-service"
        }
    )

    response = client.get("/api/logs")

    assert response.status_code == 200
    assert response.json["count"] == 1
    assert response.json["logs"][0]["message"] == "Service started"


def test_invalid_log_level_is_rejected(client):
    response = client.post(
        "/api/logs",
        json={
            "level": "CRITICAL",
            "message": "Invalid test event"
        }
    )

    assert response.status_code == 400


def test_empty_message_is_rejected(client):
    response = client.post(
        "/api/logs",
        json={
            "level": "ERROR",
            "message": "   "
        }
    )

    assert response.status_code == 400


def test_invalid_filter_is_rejected(client):
    response = client.get("/api/logs?level=CRITICAL")

    assert response.status_code == 400
