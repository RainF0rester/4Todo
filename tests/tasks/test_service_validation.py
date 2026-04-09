import pytest
from modules.tasks import service


def valid_payload():
    """
    Return a valid task payload for reuse across validation-related tests.

    This helper keeps test data consistent and makes each test easier to read.
    When a test needs an invalid case, it starts from this valid baseline and
    changes only the field under test.
    """
    return {
        "task_title": "test task",
        "task_due": "2099-01-01 10:30",
        "task_description": "test desc",
        "task_level": 1,
        "is_finished": 0,
    }


# ============================================================
# _parse_due_time
# These tests verify how the service layer parses and validates
# task_due values before they are stored or passed downstream.
# ============================================================

def test_parse_due_time_accepts_future_time():
    """
    A correctly formatted future due time should be accepted and
    normalized to include seconds.
    """
    result = service._parse_due_time("2099-01-01 10:30")
    assert result == "2099-01-01 10:30:00"


def test_parse_due_time_accepts_none():
    """
    None is allowed for task_due, which supports tasks without a due time.
    """
    result = service._parse_due_time(None)
    assert result is None


def test_parse_due_time_empty_string_returns_none():
    """
    Blank strings should be treated the same as no due time provided.
    """
    result = service._parse_due_time("   ")
    assert result is None


def test_parse_due_time_rejects_invalid_format():
    """
    Due time must follow the required YYYY-MM-DD HH:MM format.
    """
    with pytest.raises(ValueError, match="format YYYY-MM-DD HH:MM"):
        service._parse_due_time("2026/01/01")


# ============================================================
# _normalize
# These tests verify input normalization for task creation.
# They ensure valid payloads are transformed correctly and
# invalid payloads are rejected early.
# ============================================================

def test_normalize_accepts_valid_payload():
    """
    A complete and valid payload should be normalized without errors.
    """
    data = service._normalize(valid_payload())

    assert data["task_title"] == "test task"
    assert data["task_due"] == "2099-01-01 10:30:00"
    assert data["task_description"] == "test desc"
    assert data["task_level"] == 1
    assert data["is_finished"] == 0


def test_normalize_rejects_empty_title():
    """
    Task title cannot be blank after trimming whitespace.
    """
    payload = valid_payload()
    payload["task_title"] = "   "

    with pytest.raises(ValueError):
        service._normalize(payload)


def test_normalize_rejects_invalid_level():
    """
    Task level outside the allowed range should be rejected.
    """
    payload = valid_payload()
    payload["task_level"] = 20

    with pytest.raises(ValueError):
        service._normalize(payload)


def test_normalize_rejects_invalid_is_finished():
    """
    is_finished must be a supported numeric/bool-like value,
    not an arbitrary string.
    """
    payload = valid_payload()
    payload["is_finished"] = "yes"

    with pytest.raises(ValueError):
        service._normalize(payload)


def test_normalize_accepts_valid_title_length():
    """
    A title at the maximum allowed length should still be accepted.
    """
    payload = valid_payload()
    payload["task_title"] = "a" * 100

    data = service._normalize(payload)

    assert data["task_title"] == "a" * 100


def test_normalize_rejects_long_title():
    """
    Titles longer than the allowed maximum should be rejected.
    """
    payload = valid_payload()
    payload["task_title"] = "a" * 101

    with pytest.raises(ValueError):
        service._normalize(payload)


def test_normalize_converts_blank_description_to_none():
    """
    Blank descriptions should be normalized to None so the stored value
    is consistent and easier to handle later.
    """
    payload = valid_payload()
    payload["task_description"] = "   "

    data = service._normalize(payload)

    assert data["task_description"] is None


def test_normalize_converts_bool_is_finished_to_int():
    """
    Boolean is_finished values should be normalized to integer flags.
    """
    payload = valid_payload()
    payload["is_finished"] = True

    data = service._normalize(payload)

    assert data["is_finished"] == 1


# ============================================================
# _validate_task_title
# These tests focus only on title validation rules.
# ============================================================

def test_validate_task_title_rejects_title_longer_than_limit():
    """
    Titles longer than the permitted limit should fail validation.
    """
    with pytest.raises(ValueError):
        service._validate_task_title("a" * 101)


# ============================================================
# _normalize_update
# These tests verify update payload normalization. Update payloads
# differ from create payloads because partial updates are allowed.
# ============================================================

def test_normalize_update_accepts_empty_payload():
    """
    An empty update payload should return an empty dict at this stage.
    Higher-level service methods may still reject it later.
    """
    data = service._normalize_update({})
    assert data == {}


def test_normalize_update_accepts_title():
    """
    A valid updated title should be preserved after normalization.
    """
    data = service._normalize_update({"task_title": "new"})
    assert data["task_title"] == "new"


def test_normalize_update_rejects_invalid_level():
    """
    Invalid task_level values should still be rejected in update mode.
    """
    with pytest.raises(ValueError):
        service._normalize_update({"task_level": 20})


def test_normalize_update_rejects_invalid_is_finished():
    """
    Invalid is_finished values should be rejected during updates too.
    """
    with pytest.raises(ValueError):
        service._normalize_update({"is_finished": "yes"})


def test_normalize_update_converts_blank_description_to_none():
    """
    Blank updated descriptions should be normalized to None.
    """
    data = service._normalize_update({"task_description": "   "})
    assert data["task_description"] is None


def test_normalize_update_converts_bool_is_finished_to_int():
    """
    Boolean update values for is_finished should be normalized to integer flags.
    """
    data = service._normalize_update({"is_finished": True})
    assert data["is_finished"] == 1