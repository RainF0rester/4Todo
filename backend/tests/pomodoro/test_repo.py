import pytest
from datetime import date
from backend.modules.pomodoro import repo
from backend.modules.pomodoro.models import Pomodoro


TODAY = date.today().isoformat()


def test_upsert_pomodoro_creates_new_record(session):
    result = repo.upsert_pomodoro(session, user_id=1, date=TODAY)
    assert result is not None
    assert result.user_id == 1
    assert result.date == TODAY
    assert result.count == 1


def test_upsert_pomodoro_increments_existing_record(session):
    repo.upsert_pomodoro(session, user_id=1, date=TODAY)
    repo.upsert_pomodoro(session, user_id=1, date=TODAY)
    result = repo.upsert_pomodoro(session, user_id=1, date=TODAY)
    assert result.count == 3


def test_upsert_pomodoro_is_user_scoped(session):
    repo.upsert_pomodoro(session, user_id=1, date=TODAY)
    repo.upsert_pomodoro(session, user_id=1, date=TODAY)
    result_user2 = repo.upsert_pomodoro(session, user_id=2, date=TODAY)
    assert result_user2.count == 1


def test_upsert_pomodoro_is_date_scoped(session):
    repo.upsert_pomodoro(session, user_id=1, date="2026-01-01")
    result = repo.upsert_pomodoro(session, user_id=1, date="2026-01-02")
    assert result.count == 1


def test_get_by_date_returns_record(session):
    repo.upsert_pomodoro(session, user_id=1, date=TODAY)
    result = repo.get_by_date(session, user_id=1, date=TODAY)
    assert result is not None
    assert result.count == 1


def test_get_by_date_returns_none_when_no_record(session):
    result = repo.get_by_date(session, user_id=1, date=TODAY)
    assert result is None


def test_get_by_date_is_user_scoped(session):
    repo.upsert_pomodoro(session, user_id=1, date=TODAY)
    result = repo.get_by_date(session, user_id=2, date=TODAY)
    assert result is None


def test_list_by_range_returns_records_in_range(session):
    repo.upsert_pomodoro(session, user_id=1, date="2026-01-01")
    repo.upsert_pomodoro(session, user_id=1, date="2026-01-15")
    repo.upsert_pomodoro(session, user_id=1, date="2026-01-31")
    results = repo.list_by_range(session, user_id=1, start_date="2026-01-01", end_date="2026-01-31")
    assert len(results) == 3


def test_list_by_range_excludes_out_of_range(session):
    repo.upsert_pomodoro(session, user_id=1, date="2025-12-31")
    repo.upsert_pomodoro(session, user_id=1, date="2026-01-15")
    repo.upsert_pomodoro(session, user_id=1, date="2026-02-01")
    results = repo.list_by_range(session, user_id=1, start_date="2026-01-01", end_date="2026-01-31")
    assert len(results) == 1
    assert results[0].date == "2026-01-15"


def test_list_by_range_is_user_scoped(session):
    repo.upsert_pomodoro(session, user_id=1, date="2026-01-01")
    repo.upsert_pomodoro(session, user_id=2, date="2026-01-01")
    results = repo.list_by_range(session, user_id=1, start_date="2026-01-01", end_date="2026-01-31")
    assert len(results) == 1


def test_list_by_range_returns_empty_when_no_records(session):
    results = repo.list_by_range(session, user_id=1, start_date="2026-01-01", end_date="2026-01-31")
    assert results == []
