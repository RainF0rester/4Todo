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


# ============================================================
# _parse_due_time
# ============================================================

def test_parse_due_time_accepts_future_time():
    result = service._parse_due_time("2099-01-01 10:30")
    assert result == "2099-01-01 10:30:00"


def test_parse_due_time_accepts_none():
    result = service._parse_due_time(None)
    assert result is None


def test_parse_due_time_empty_string_returns_none():
    result = service._parse_due_time("   ")
    assert result is None


def test_parse_due_time_rejects_invalid_format():
    with pytest.raises(ValueError, match="format YYYY-MM-DD HH:MM"):
        service._parse_due_time("2026/01/01")


def test_parse_due_time_rejects_invalid_time_string():
    with pytest.raises(ValueError):
        service._parse_due_time("invalid")


# ============================================================
# _normalize
# ============================================================

def test_normalize_accepts_valid_payload():
    data = service._normalize(valid_payload())

    assert data["task_title"] == "test task"
    assert data["task_due"] == "2099-01-01 10:30:00"
    assert data["task_description"] == "test desc"
    assert data["task_level"] == 1
    assert data["is_finished"] == 0


def test_normalize_allows_none_due_time():
    payload = valid_payload()
    payload["task_due"] = None

    data = service._normalize(payload)

    assert data["task_due"] is None


def test_normalize_rejects_empty_title():
    payload = valid_payload()
    payload["task_title"] = "   "

    with pytest.raises(ValueError):
        service._normalize(payload)


def test_normalize_rejects_invalid_level():
    payload = valid_payload()
    payload["task_level"] = 20

    with pytest.raises(ValueError):
        service._normalize(payload)


def test_normalize_rejects_invalid_is_finished():
    payload = valid_payload()
    payload["is_finished"] = "yes"

    with pytest.raises(ValueError):
        service._normalize(payload)


def test_normalize_accepts_valid_title_length():
    payload = valid_payload()
    payload["task_title"] = "a" * 100

    data = service._normalize(payload)

    assert data["task_title"] == "a" * 100


def test_normalize_rejects_long_title():
    payload = valid_payload()
    payload["task_title"] = "a" * 101

    with pytest.raises(ValueError):
        service._normalize(payload)


def test_normalize_converts_blank_description_to_none():
    payload = valid_payload()
    payload["task_description"] = "   "

    data = service._normalize(payload)

    assert data["task_description"] is None


def test_normalize_converts_bool_is_finished_to_int():
    payload = valid_payload()
    payload["is_finished"] = True

    data = service._normalize(payload)

    assert data["is_finished"] == 1


# ============================================================
# _validate_task_title
# ============================================================

def test_validate_task_title_rejects_title_longer_than_limit():
    with pytest.raises(ValueError):
        service._validate_task_title("a" * 101)


# ============================================================
# _normalize_update
# ============================================================

def test_normalize_update_accepts_empty_payload():
    data = service._normalize_update({})
    assert data == {}


def test_normalize_update_accepts_title():
    data = service._normalize_update({"task_title": "new"})
    assert data["task_title"] == "new"


def test_normalize_update_rejects_invalid_level():
    with pytest.raises(ValueError):
        service._normalize_update({"task_level": 20})


def test_normalize_update_rejects_invalid_is_finished():
    with pytest.raises(ValueError):
        service._normalize_update({"is_finished": "yes"})


def test_normalize_update_converts_blank_description_to_none():
    data = service._normalize_update({"task_description": "   "})
    assert data["task_description"] is None


def test_normalize_update_converts_bool_is_finished_to_int():
    data = service._normalize_update({"is_finished": True})
    assert data["is_finished"] == 1