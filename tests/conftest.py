"""
Test fixtures for the Flask application.

Note:
This file was generated with assistance from an AI tool (ChatGPT) and
reviewed/modified by the project author before inclusion in the repository.
"""

import pytest
from app import create_app


@pytest.fixture(scope="session")
def app():
    """
    Create a Flask application instance for the entire test session.

    Using session scope prevents Flask from re-registering blueprints
    multiple times across tests.
    """
    app = create_app()
    app.config.update(
        TESTING=True
    )
    return app


@pytest.fixture()
def client(app):
    """
    Provide a Flask test client for each test.
    """
    return app.test_client()