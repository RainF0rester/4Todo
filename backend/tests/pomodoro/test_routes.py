import pytest
from unittest.mock import MagicMock, patch
from datetime import date


TODAY = date.today().isoformat()


def _auth_patch():
    return patch(
        "backend.utils.auth_decorator.validate_token",
        return_value={"state": "active", "payload": {"user_id": 1}},
    )


def _dummy_record(count=1):
    record = MagicMock()
    record.to_json.return_value = {
        "id": 1,
        "user_id": 1,
        "date": TODAY,
        "count": count,
    }
    return record


# =========================
# POST /pomodoro
# =========================

def test_log_pomodoro_success(client):
    with _auth_patch(), patch("backend.modules.pomodoro.service.log_pomodoro") as mock_log:
        mock_log.return_value = _dummy_record(count=1)
        resp = client.post("/pomodoro", headers={"Authorization": "Bearer token"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["count"] == 1
        assert data["date"] == TODAY


def test_log_pomodoro_increments_count(client):
    with _auth_patch(), patch("backend.modules.pomodoro.service.log_pomodoro") as mock_log:
        mock_log.return_value = _dummy_record(count=3)
        resp = client.post("/pomodoro", headers={"Authorization": "Bearer token"})
        assert resp.status_code == 201
        assert resp.get_json()["count"] == 3


def test_log_pomodoro_requires_auth(client):
    resp = client.post("/pomodoro")
    assert resp.status_code == 401


# =========================
# GET /pomodoro/today
# =========================

def test_get_today_returns_record(client):
    with _auth_patch(), patch("backend.modules.pomodoro.service.get_today") as mock_get:
        mock_get.return_value = _dummy_record(count=2)
        resp = client.get("/pomodoro/today", headers={"Authorization": "Bearer token"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["count"] == 2
        assert data["date"] == TODAY


def test_get_today_returns_zero_when_no_record(client):
    with _auth_patch(), patch("backend.modules.pomodoro.service.get_today", return_value=None):
        resp = client.get("/pomodoro/today", headers={"Authorization": "Bearer token"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["count"] == 0
        assert data["id"] is None


def test_get_today_requires_auth(client):
    resp = client.get("/pomodoro/today")
    assert resp.status_code == 401


# =========================
# GET /pomodoro/range
# =========================

def test_get_range_success(client):
    records = [_dummy_record(count=i + 1) for i in range(3)]
    with _auth_patch(), patch("backend.modules.pomodoro.service.get_range") as mock_range:
        mock_range.return_value = records
        resp = client.get(
            "/pomodoro/range?start_date=2026-01-01&end_date=2026-01-31",
            headers={"Authorization": "Bearer token"},
        )
        assert resp.status_code == 200
        assert len(resp.get_json()) == 3


def test_get_range_returns_empty_list(client):
    with _auth_patch(), patch("backend.modules.pomodoro.service.get_range", return_value=[]):
        resp = client.get(
            "/pomodoro/range?start_date=2026-01-01&end_date=2026-01-31",
            headers={"Authorization": "Bearer token"},
        )
        assert resp.status_code == 200
        assert resp.get_json() == []


def test_get_range_invalid_date_returns_400(client):
    with _auth_patch(), patch("backend.modules.pomodoro.service.get_range") as mock_range:
        mock_range.side_effect = ValueError("Invalid date format")
        resp = client.get(
            "/pomodoro/range?start_date=bad-date&end_date=2026-01-31",
            headers={"Authorization": "Bearer token"},
        )
        assert resp.status_code == 400


def test_get_range_start_after_end_returns_400(client):
    with _auth_patch(), patch("backend.modules.pomodoro.service.get_range") as mock_range:
        mock_range.side_effect = ValueError("start_date must be before end_date")
        resp = client.get(
            "/pomodoro/range?start_date=2026-02-01&end_date=2026-01-01",
            headers={"Authorization": "Bearer token"},
        )
        assert resp.status_code == 400


def test_get_range_requires_auth(client):
    resp = client.get("/pomodoro/range?start_date=2026-01-01&end_date=2026-01-31")
    assert resp.status_code == 401
