"""Tests for the require_auth decorator."""

from unittest.mock import patch

from flask import g

from backend.utils.auth_decorator import require_auth


def _build_test_client(route_func):
    from backend.app import create_app

    app = create_app()
    app.route('/test_auth')(route_func)
    return app.test_client()


class TestRequireAuth:
    def test_require_auth_missing_header(self):
        @require_auth
        def test_route():
            return {"ok": True}

        client = _build_test_client(test_route)
        response = client.get('/test_auth')

        assert response.status_code == 401
        assert 'Missing authorization token' in response.json.get('message', '')

    def test_require_auth_invalid_scheme(self):
        @require_auth
        def test_route():
            return {"ok": True}

        client = _build_test_client(test_route)
        response = client.get('/test_auth', headers={'Authorization': 'Basic invalid_token'})

        assert response.status_code == 401
        assert 'Invalid authorization' in response.json.get('message', '')

    def test_require_auth_malformed_header(self):
        @require_auth
        def test_route():
            return {"ok": True}

        client = _build_test_client(test_route)
        response = client.get('/test_auth', headers={'Authorization': 'onlytoken'})

        assert response.status_code == 401
        assert 'Invalid authorization' in response.json.get('message', '')

    @patch('backend.utils.auth_decorator.validate_token')
    def test_require_auth_valid_token(self, mock_validate):
        mock_validate.return_value = {
            'state': 'active',
            'payload': {
                'user_id': 123,
                'username': 'testuser',
            },
        }

        @require_auth
        def test_route():
            return {"user_id": g.user_id}

        client = _build_test_client(test_route)
        response = client.get('/test_auth', headers={'Authorization': 'Bearer valid_token'})

        assert response.status_code == 200
        assert response.json['user_id'] == 123

    @patch('backend.utils.auth_decorator.validate_token')
    def test_require_auth_refreshable_token(self, mock_validate):
        mock_validate.return_value = {
            'state': 'refreshable',
            'payload': {'user_id': 123},
        }

        @require_auth
        def test_route():
            return {"ok": True}

        client = _build_test_client(test_route)
        response = client.get('/test_auth', headers={'Authorization': 'Bearer expired_token'})

        assert response.status_code == 401
        assert 'Token expired' in response.json.get('message', '')

    @patch('backend.utils.auth_decorator.validate_token')
    def test_require_auth_invalid_token(self, mock_validate):
        from backend.utils.jwt_utils import TokenError

        mock_validate.side_effect = TokenError("Invalid token")

        @require_auth
        def test_route():
            return {"ok": True}

        client = _build_test_client(test_route)
        response = client.get('/test_auth', headers={'Authorization': 'Bearer invalid_token'})

        assert response.status_code == 401
        assert 'Invalid token' in response.json.get('message', '')


