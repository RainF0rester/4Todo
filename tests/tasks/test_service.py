import pytest
from modules.tasks import service


def valid_payload():
    return {
        "task_title": "test task",
        "task_due": "2099-01-01 10:30",
        "task_description": "test desc",
        "task_level": 1,
        "is_finished": 0,
    }


def test_parse_due_time_accepts_future_time():
    result = service._parse_due_time("2099-01-01 10:30")
    assert result == "2099-01-01 10:30"


def test_parse_due_time_accepts_none():
    result = service._parse_due_time(None)
    assert result is None


def test_parse_due_time_rejects_past_time():
    with pytest.raises(ValueError, match="Task due time cannot be in the past"):
        service._parse_due_time("2020-01-01 10:30")


def test_normalize_accepts_valid_payload():
    data = service._normalize(valid_payload())
    assert data["task_title"] == "test task"
    assert data["task_due"] == "2099-01-01 10:30"
    assert data["task_description"] == "test desc"
    assert data["task_level"] == 1
    assert data["is_finished"] == 0


def test_normalize_rejects_empty_title():
    payload = valid_payload()
    payload["task_title"] = "   "

    with pytest.raises(ValueError, match="Task title is required"):
        service._normalize(payload)


def test_normalize_rejects_past_due_time():
    payload = valid_payload()
    payload["task_due"] = "2020-01-01 10:30"

    with pytest.raises(ValueError, match="Task due time cannot be in the past"):
        service._normalize(payload)

def test_normalize_accepts_valid_title_length():
    payload = {
        "task_title": "a" * 100,
        "task_due": "2099-01-01 10:30",
        "task_description": "desc",
        "task_level": 1,
        "is_finished": 0,
    }

    data = service._normalize(payload)

    assert data["task_title"] == "a" * 100

def test_normalize_rejects_long_title():
    payload = {
        "task_title": "a" * 101,
        "task_due": "2099-01-01 10:30",
        "task_description": "desc",
        "task_level": 1,
        "is_finished": 0,
    }

    with pytest.raises(ValueError, match="Task title must not exceed 100 characters"):
        service._normalize(payload)

def test_validate_title_in_update():
    with pytest.raises(ValueError):
        service._validate_task_title("a" * 101)