import pytest
from app import create_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modules.tasks.models import Base


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