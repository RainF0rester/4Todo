import pytest
from backend.app import create_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.modules.tasks.models import Base
from backend.modules.users.models import User
from backend.utils.jwt_utils import create_token


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config.update(TESTING=True)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def test_user(session):
    user = User(
        username="lucia_test",
        email="lucia_test@ad.unsw.edu.au",
        password_hash="test_hash",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture()
def auth_headers(test_user):
    token = create_token(
        test_user.id,
        test_user.username,
        test_user.email,
    )
    return {
        "Authorization": f"Bearer {token}"
    }