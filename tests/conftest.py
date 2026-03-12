"""
Test fixtures for the Flask application.

Note:
This file was generated with assistance from an AI tool (ChatGPT) and
reviewed/modified by the project author before inclusion in the repository.
"""

import pytest
from app import create_app


@pytest.fixture
def app():
    """
    Create and configure a Flask application instance for testing.

    The TESTING flag enables Flask's testing mode, which:
    - Propagates exceptions instead of handling them internally
    - Provides better error reporting for tests
    """
    app = create_app()
    app.config.update({
        "TESTING": True
    })
    return app


@pytest.fixture
def client(app):
    """
    Create a Flask test client for sending HTTP requests to the application.

    The test client simulates requests to the Flask app without running
    a real server, allowing tests to call endpoints such as:

        client.get("/tasks")
        client.post("/tasks", json={...})
    """
    return app.test_client()