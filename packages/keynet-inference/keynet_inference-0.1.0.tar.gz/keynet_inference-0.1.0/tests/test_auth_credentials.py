"""Tests for the credentials module"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from keynet_inference.auth.credentials import CredentialManager


class TestCredentialManager:
    """Tests for CredentialManager"""

    @pytest.fixture
    def temp_home(self):
        """Create a temporary home directory"""
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch.dict(os.environ, {"HOME": temp_dir}),
            patch("pathlib.Path.home", return_value=Path(temp_dir)),
        ):
            yield Path(temp_dir)

    @pytest.fixture
    def cred_manager(self, temp_home):
        """Create a CredentialManager instance with temp home"""
        return CredentialManager()

    def test_init_creates_config_dir(self, temp_home, cred_manager):
        """Test that initialization creates the .keynet directory"""
        config_dir = temp_home / ".keynet"
        assert config_dir.exists()
        assert config_dir.is_dir()

    def test_save_and_get_credentials(self, cred_manager):
        """Test saving and retrieving credentials"""
        server = "api.keynet.io"
        username = "testuser"
        password = "testpass123"

        # Save credentials
        cred_manager.save_credentials(server, username, password)

        # Retrieve credentials
        result = cred_manager.get_credentials(server)
        assert result is not None
        retrieved_username, retrieved_password = result
        assert retrieved_username == username
        assert retrieved_password == password

    def test_get_credentials_nonexistent_server(self, cred_manager):
        """Test getting credentials for a server that doesn't exist"""
        result = cred_manager.get_credentials("nonexistent.server.com")
        assert result is None

    def test_list_servers(self, cred_manager):
        """Test listing all servers with saved credentials"""
        servers = ["api.keynet.io", "staging.keynet.io", "dev.keynet.io"]

        # Save credentials for multiple servers
        for i, server in enumerate(servers):
            cred_manager.save_credentials(server, f"user{i}", f"pass{i}")

        # List servers
        listed_servers = cred_manager.list_servers()
        assert set(listed_servers) == set(servers)

    def test_remove_specific_server_credentials(self, cred_manager):
        """Test removing credentials for a specific server"""
        server1 = "api.keynet.io"
        server2 = "staging.keynet.io"

        # Save credentials for two servers
        cred_manager.save_credentials(server1, "user1", "pass1")
        cred_manager.save_credentials(server2, "user2", "pass2")

        # Remove credentials for server1
        cred_manager.remove_credentials(server1)

        # Check that server1 is removed but server2 remains
        assert cred_manager.get_credentials(server1) is None
        assert cred_manager.get_credentials(server2) is not None

    def test_remove_all_credentials(self, cred_manager):
        """Test removing all credentials"""
        # Save credentials
        cred_manager.save_credentials("api.keynet.io", "user", "pass")

        # Remove all credentials
        cred_manager.remove_credentials()

        # Check that files are removed
        assert not cred_manager.config_file.exists()
        assert not cred_manager.key_file.exists()

        # Check that no servers are listed
        assert cred_manager.list_servers() == []

    def test_get_active_server(self, cred_manager):
        """Test getting the most recently used server"""
        servers = ["api1.keynet.io", "api2.keynet.io", "api3.keynet.io"]

        # Save credentials in order
        for server in servers:
            cred_manager.save_credentials(server, "user", "pass")

        # The last server should be the active one
        assert cred_manager.get_active_server() == servers[-1]

    def test_get_active_server_no_credentials(self, cred_manager):
        """Test getting active server when no credentials exist"""
        assert cred_manager.get_active_server() is None

    def test_machine_binding(self, cred_manager):
        """Test that credentials are bound to the machine"""
        server = "api.keynet.io"
        username = "testuser"
        password = "testpass"

        # Save credentials
        cred_manager.save_credentials(server, username, password)

        # Create new instance with different machine ID
        new_cred_manager = CredentialManager()
        with patch.object(
            new_cred_manager, "_get_machine_id", return_value="different-machine-id"
        ):
            # Should not be able to decrypt with different machine ID
            # Will raise InvalidToken error from Fernet
            from cryptography.fernet import InvalidToken

            with pytest.raises(InvalidToken):
                new_cred_manager.get_credentials(server)

    def test_corrupted_credentials_file(self, cred_manager):
        """Test handling of corrupted credentials file"""
        # Create a corrupted file
        cred_manager.config_file.parent.mkdir(exist_ok=True)
        cred_manager.config_file.write_text("not valid json")

        # Should return None instead of crashing
        result = cred_manager.get_credentials("api.keynet.io")
        assert result is None

        # List servers should return empty list
        assert cred_manager.list_servers() == []

    def test_windows_compatibility(self, cred_manager):
        """Test that chmod failures are handled gracefully"""
        server = "api.keynet.io"

        # Mock chmod to raise OSError (simulating Windows)
        with patch(
            "pathlib.Path.chmod", side_effect=OSError("Operation not supported")
        ):
            # Should not raise exception
            cred_manager.save_credentials(server, "user", "pass")

            # Should still be able to retrieve credentials
            result = cred_manager.get_credentials(server)
            assert result is not None

    def test_update_existing_credentials(self, cred_manager):
        """Test updating credentials for an existing server"""
        server = "api.keynet.io"

        # Save initial credentials
        cred_manager.save_credentials(server, "user1", "pass1")

        # Update with new credentials
        cred_manager.save_credentials(server, "user2", "pass2")

        # Should get the updated credentials
        result = cred_manager.get_credentials(server)
        assert result is not None
        username, password = result
        assert username == "user2"
        assert password == "pass2"

    def test_salt_persistence(self, cred_manager):
        """Test that salt is persisted across sessions"""
        server = "api.keynet.io"
        username = "testuser"
        password = "testpass"

        # Save credentials
        cred_manager.save_credentials(server, username, password)

        # Create new instance (simulating new session)
        new_cred_manager = CredentialManager()

        # Should be able to retrieve credentials
        result = new_cred_manager.get_credentials(server)
        assert result is not None
        retrieved_username, retrieved_password = result
        assert retrieved_username == username
        assert retrieved_password == password

    @patch("uuid.getnode", side_effect=Exception("MAC retrieval failed"))
    def test_mac_address_failure_handling(self, mock_getnode, cred_manager):
        """Test that MAC address retrieval failure is handled"""
        # Should still work without MAC address
        server = "api.keynet.io"
        cred_manager.save_credentials(server, "user", "pass")

        result = cred_manager.get_credentials(server)
        assert result is not None
