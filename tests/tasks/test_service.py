import pytest
from unittest.mock import patch, MagicMock
from modules.tasks import service


def valid_payload():
    return {
        "task_title": "test task",
        "task_due": "2099-01-01 10:30",
        "task_description": "test desc",
        "task_level": 1,
        "is_finished": 0,
    }


# =========================
# PARSE DUE TIME
# =========================

def test_parse_due_time_accepts_future_time():
    result = service._parse_due_time("2099-01-01 10:30")
    assert result == "2099-01-01 10:30"


def test_parse_due_time_accepts_none():
    result = service._parse_due_time(None)
    assert result is None


def test_parse_due_time_empty_string():
    result = service._parse_due_time("   ")
    assert result is None


def test_parse_due_time_rejects_past_time():
    with pytest.raises(ValueError, match="Task due time cannot be in the past"):
        service._parse_due_time("2020-01-01 10:30")


def test_parse_due_time_invalid_format():
    with pytest.raises(ValueError, match="format YYYY-MM-DD HH:MM"):
        service._parse_due_time("2026/01/01")


# =========================
# NORMALIZE
# =========================

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

    with pytest.raises(ValueError):
        service._normalize(payload)


def test_normalize_rejects_past_due_time():
    payload = valid_payload()
    payload["task_due"] = "2020-01-01 10:30"

    with pytest.raises(ValueError):
        service._normalize(payload)


def test_normalize_invalid_level():
    payload = valid_payload()
    payload["task_level"] = 20

    with pytest.raises(ValueError):
        service._normalize(payload)


def test_normalize_invalid_is_finished():
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


def test_normalize_description_strip_to_none():
    payload = valid_payload()
    payload["task_description"] = "   "

    data = service._normalize(payload)

    assert data["task_description"] is None


def test_normalize_is_finished_bool():
    payload = valid_payload()
    payload["is_finished"] = True

    data = service._normalize(payload)

    assert data["is_finished"] == 1


# =========================
# VALIDATE TITLE
# =========================

def test_validate_title_in_update():
    with pytest.raises(ValueError):
        service._validate_task_title("a" * 101)


# =========================
# NORMALIZE UPDATE
# =========================

def test_normalize_update_empty():
    data = service._normalize_update({})
    assert data == {}


def test_normalize_update_title():
    data = service._normalize_update({"task_title": "new"})
    assert data["task_title"] == "new"


def test_normalize_update_invalid_level():
    with pytest.raises(ValueError):
        service._normalize_update({"task_level": 20})


def test_normalize_update_invalid_is_finished():
    with pytest.raises(ValueError):
        service._normalize_update({"is_finished": "yes"})


def test_normalize_update_description_strip():
    data = service._normalize_update({"task_description": "   "})
    assert data["task_description"] is None


def test_normalize_update_is_finished_bool():
    data = service._normalize_update({"is_finished": True})
    assert data["is_finished"] == 1


# =========================
# CREATE
# =========================

def test_create_task_success():
    with patch("modules.tasks.repo.create_task") as mock_create:
        mock_task = MagicMock()
        mock_create.return_value = mock_task

        result = service.create_task(None, valid_payload())

        assert result == mock_task
        mock_create.assert_called_once()


def test_create_task_invalid_payload():
    with pytest.raises(ValueError):
        service.create_task(None, {"task_title": "   "})


# =========================
# UPDATE
# =========================

def test_update_task_success():
    fake_task = MagicMock()
    fake_task.is_deleted = 0

    with patch("modules.tasks.repo.get_task", return_value=fake_task), \
         patch("modules.tasks.repo.update_task", return_value=fake_task):

        result = service.update_task(None, 1, {"task_title": "new"})

        assert result == fake_task
        assert fake_task.task_title == "new"


def test_update_task_not_found():
    with patch("modules.tasks.repo.get_task", return_value=None):
        with pytest.raises(ValueError):
            service.update_task(None, 1, {"task_title": "new"})


def test_update_task_deleted():
    fake_task = MagicMock()
    fake_task.is_deleted = 1

    with patch("modules.tasks.repo.get_task", return_value=fake_task):
        with pytest.raises(ValueError):
            service.update_task(None, 1, {"task_title": "new"})


def test_update_task_empty_payload():
    fake_task = MagicMock()
    fake_task.is_deleted = 0

    with patch("modules.tasks.repo.get_task", return_value=fake_task):
        with pytest.raises(ValueError):
            service.update_task(None, 1, {})


# =========================
# GET
# =========================

def test_get_task_success():
    fake_task = MagicMock()
    fake_task.is_deleted = 0

    with patch("modules.tasks.repo.get_task", return_value=fake_task):
        result = service.get_task(None, 1)
        assert result == fake_task


def test_get_task_not_found():
    with patch("modules.tasks.repo.get_task", return_value=None):
        with pytest.raises(ValueError):
            service.get_task(None, 1)


def test_get_task_deleted():
    fake_task = MagicMock()
    fake_task.is_deleted = 1

    with patch("modules.tasks.repo.get_task", return_value=fake_task):
        with pytest.raises(ValueError):
            service.get_task(None, 1)


# =========================
# DELETE / RESTORE
# =========================

def test_soft_delete_task_success():
    with patch("modules.tasks.repo.soft_delete_task", return_value=True):
        service.soft_delete_task(None, 1)


def test_soft_delete_task_not_found():
    with patch("modules.tasks.repo.soft_delete_task", return_value=False):
        with pytest.raises(ValueError):
            service.soft_delete_task(None, 1)


def test_restore_task_success():
    with patch("modules.tasks.repo.restore_task", return_value=True):
        service.restore_task(None, 1)


def test_restore_task_not_found():
    with patch("modules.tasks.repo.restore_task", return_value=False):
        with pytest.raises(ValueError):
            service.restore_task(None, 1)


# =========================
# LIST
# =========================

def test_list_tasks():
    fake_list = [MagicMock(), MagicMock()]

    with patch("modules.tasks.repo.list_tasks", return_value=fake_list):
        result = service.list_tasks(None)

        assert result == fake_list


def test_list_tasks_include_deleted():
    fake_list = [MagicMock()]

    with patch("modules.tasks.repo.list_tasks", return_value=fake_list) as mock_list:
        result = service.list_tasks(None, include_deleted=True)

        assert result == fake_list
        mock_list.assert_called_once_with(None, include_deleted=True)