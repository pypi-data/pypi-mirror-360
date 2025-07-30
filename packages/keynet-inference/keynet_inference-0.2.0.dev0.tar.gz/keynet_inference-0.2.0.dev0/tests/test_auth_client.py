"""Tests for the auth client module"""

import base64
from unittest.mock import Mock, patch

import pytest

from keynet_inference.auth.client import AuthClient
from keynet_inference.auth.credentials import CredentialManager


class TestAuthClient:
    """Tests for AuthClient"""

    @pytest.fixture
    def auth_client(self):
        """Create an AuthClient instance"""
        return AuthClient("api.keynet.io")

    def test_init(self, auth_client):
        """Test AuthClient initialization"""
        assert auth_client.server_domain == "api.keynet.io"
        assert isinstance(auth_client.credential_manager, CredentialManager)

    def test_authenticate_success(self, auth_client):
        """Test successful authentication"""
        username = "testuser"
        password = "testpass"

        success, token = auth_client.authenticate(username, password)

        assert success is True
        assert token is not None
        # Verify token format (base64 encoded)
        decoded = base64.b64decode(token).decode()
        assert username in decoded
        assert auth_client.server_domain in decoded

    def test_authenticate_empty_credentials(self, auth_client):
        """Test authentication with empty credentials"""
        # Empty username
        success, result = auth_client.authenticate("", "password")
        assert success is False
        assert result == "Invalid credentials"

        # Empty password
        success, result = auth_client.authenticate("username", "")
        assert success is False
        assert result == "Invalid credentials"

    def test_validate_token_valid(self, auth_client):
        """Test token validation with valid token"""
        token = "valid_token_123"
        assert auth_client.validate_token(token) is True

    def test_validate_token_invalid(self, auth_client):
        """Test token validation with invalid token"""
        assert auth_client.validate_token("") is False

    def test_refresh_token_valid(self, auth_client):
        """Test refreshing a valid token"""
        token = "valid_token_123"
        success, new_token = auth_client.refresh_token(token)

        assert success is True
        assert new_token == token  # Mock returns same token

    def test_refresh_token_invalid(self, auth_client):
        """Test refreshing an invalid token"""
        with patch.object(auth_client, "validate_token", return_value=False):
            success, result = auth_client.refresh_token("invalid_token")

            assert success is False
            assert result == "Invalid or expired token"

    def test_get_stored_token_with_credentials(self, auth_client):
        """Test getting stored token when credentials exist"""
        mock_creds = ("testuser", "testpass")

        with patch.object(
            auth_client.credential_manager, "get_credentials", return_value=mock_creds
        ):
            token = auth_client.get_stored_token()

            assert token is not None
            # Verify it's a valid base64 token
            decoded = base64.b64decode(token).decode()
            assert "testuser" in decoded

    def test_get_stored_token_no_credentials(self, auth_client):
        """Test getting stored token when no credentials exist"""
        with patch.object(
            auth_client.credential_manager, "get_credentials", return_value=None
        ):
            token = auth_client.get_stored_token()
            assert token is None

    def test_get_stored_token_auth_failure(self, auth_client):
        """Test getting stored token when authentication fails"""
        mock_creds = ("testuser", "testpass")

        with (
            patch.object(
                auth_client.credential_manager,
                "get_credentials",
                return_value=mock_creds,
            ),
            patch.object(
                auth_client, "authenticate", return_value=(False, "Auth failed")
            ),
        ):
            token = auth_client.get_stored_token()
            assert token is None

    @patch("requests.post")
    def test_future_real_authentication(self, mock_post, auth_client):
        """Test placeholder for future real authentication implementation"""
        # This test documents the expected API call format
        # Currently not implemented, but shows the intended behavior

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "real_jwt_token_here"}
        mock_post.return_value = mock_response

        # In the future, authenticate should make this call:
        # response = requests.post(
        #     f"https://{auth_client.server_domain}/api/auth/login",
        #     json={"username": username, "password": password}
        # )

        # For now, just verify the mock behavior is as expected
        assert auth_client.authenticate("user", "pass")[0] is True
