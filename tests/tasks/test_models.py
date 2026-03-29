from modules.tasks.models import Task


def create_task():
    return Task(
        id=1,
        task_title="test",
        task_due="2099-01-01",
        task_description="desc",
        task_level=1,
        is_finished=0,
        is_deleted=0,
    )


def test_to_dict():
    task = create_task()

    data = task.to_dict()

    assert data["id"] == 1
    assert data["task_title"] == "test"
    assert data["task_due"] == "2099-01-01"
    assert data["task_description"] == "desc"
    assert data["task_level"] == 1
    assert data["is_finished"] == 0
    assert data["is_deleted"] == 0

    assert "created_at" in data
    assert "updated_at" in data


def test_to_json():
    task = create_task()

    data = task.to_json()

    assert data == {
        "id": 1,
        "task_title": "test",
        "task_due": "2099-01-01",
        "task_description": "desc",
        "task_level": 1,
        "is_finished": 0,
    }