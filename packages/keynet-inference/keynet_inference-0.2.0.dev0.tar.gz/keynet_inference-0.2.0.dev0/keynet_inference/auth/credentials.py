"""
Secure credential storage and management

This module handles the secure storage of user credentials using
encryption and platform-specific security measures.
"""

import base64
import contextlib
import json
import os
import platform
import uuid
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CredentialManager:
    """
    Manages secure storage of Keynet credentials

    Security features:
    - Passwords encrypted using Fernet (AES-128 in CBC mode with HMAC)
    - Encryption key derived from machine-specific characteristics
    - PBKDF2 with 480,000 iterations (OWASP 2023 recommendation)
    - 256-bit salt for key derivation
    - Files stored with restrictive permissions (0o600)
    - Machine-bound: credentials cannot be copied to another system

    Note: This provides reasonable security for local credential storage.
    For higher security requirements, consider using OS keyring services.
    """

    def __init__(self):
        self.config_dir = Path.home() / ".keynet"
        self.config_file = self.config_dir / "credentials.json"
        self.key_file = self.config_dir / ".keynet.key"
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure config directory exists with proper permissions"""
        self.config_dir.mkdir(mode=0o700, exist_ok=True)

    def _get_machine_id(self) -> str:
        """Get a unique machine identifier"""
        # Combine multiple factors for uniqueness
        factors = [
            platform.node(),  # hostname
            platform.machine(),  # machine type
            platform.processor(),  # processor info
            str(Path.home()),  # home directory path
        ]

        # Try to get MAC address
        try:
            mac = ":".join(
                [
                    f"{(uuid.getnode() >> elements) & 0xFF:02x}"
                    for elements in range(0, 2 * 6, 2)
                ][::-1]
            )
            factors.append(mac)
        except Exception:
            # MAC address retrieval may fail on some systems
            pass

        return "|".join(factors)

    def _derive_key(self, salt: bytes) -> bytes:
        """Derive encryption key from machine-specific data"""
        # Use PBKDF2 to derive key from machine ID
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # OWASP 2023 recommendation
        )

        machine_id = self._get_machine_id()
        key_material = kdf.derive(machine_id.encode())

        # Encode for Fernet
        return base64.urlsafe_b64encode(key_material)

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key for credentials"""
        salt_file = self.config_dir / ".salt"

        if self.key_file.exists() and salt_file.exists():
            # Read salt and derive key
            salt = salt_file.read_bytes()
            return self._derive_key(salt)
        else:
            # Generate new salt
            salt = os.urandom(32)  # 256-bit salt

            # Save salt with restricted permissions
            salt_file.write_bytes(salt)
            with contextlib.suppress(OSError, AttributeError):
                # chmod may fail on Windows or some filesystems
                salt_file.chmod(0o600)

            # Create marker file to indicate key is initialized
            self.key_file.write_text("initialized")
            with contextlib.suppress(OSError, AttributeError):
                # chmod may fail on Windows or some filesystems
                self.key_file.chmod(0o600)

            return self._derive_key(salt)

    def save_credentials(self, server_domain: str, username: str, password: str):
        """Save credentials securely"""
        # Get or create encryption key
        key = self._get_or_create_key()
        fernet = Fernet(key)

        # Encrypt password
        encrypted_password = fernet.encrypt(password.encode())

        # Load existing credentials or create new
        if self.config_file.exists():
            try:
                with self.config_file.open() as f:
                    credentials = json.load(f)
            except (OSError, json.JSONDecodeError):
                # File might be corrupted or inaccessible
                credentials = {}
        else:
            credentials = {}

        # Update credentials
        credentials[server_domain] = {
            "username": username,
            "password": encrypted_password.decode("utf-8"),
        }

        # Save with restricted permissions
        with self.config_file.open("w") as f:
            json.dump(credentials, f, indent=2)
        with contextlib.suppress(OSError, AttributeError):
            # chmod may fail on Windows or some filesystems
            self.config_file.chmod(0o600)

    def get_credentials(self, server_domain: str) -> Optional[tuple[str, str]]:
        """Retrieve credentials for a server domain"""
        if not self.config_file.exists():
            return None

        try:
            with self.config_file.open() as f:
                credentials = json.load(f)

            if server_domain not in credentials:
                return None

            cred = credentials[server_domain]
            username = cred["username"]
            encrypted_password = cred["password"]

            # Decrypt password
            key = self._get_or_create_key()
            fernet = Fernet(key)
            password = fernet.decrypt(encrypted_password.encode()).decode("utf-8")

            return username, password

        except (OSError, json.JSONDecodeError, KeyError):
            # File read error, JSON parse error, or missing key
            return None

    def list_servers(self) -> list[str]:
        """List all servers with saved credentials"""
        if not self.config_file.exists():
            return []

        try:
            with self.config_file.open() as f:
                credentials = json.load(f)
            return list(credentials.keys())
        except (OSError, json.JSONDecodeError):
            # File read error or JSON parse error
            return []

    def remove_credentials(self, server_domain: str = None):
        """Remove credentials for a specific server or all servers"""
        if not self.config_file.exists():
            return

        if server_domain is None:
            # Remove all credentials
            self.config_file.unlink()
            if self.key_file.exists():
                self.key_file.unlink()
            salt_file = self.config_dir / ".salt"
            if salt_file.exists():
                salt_file.unlink()
        else:
            # Remove specific server
            try:
                with self.config_file.open() as f:
                    credentials = json.load(f)

                if server_domain in credentials:
                    del credentials[server_domain]

                    if credentials:
                        # Save remaining credentials
                        with self.config_file.open("w") as f:
                            json.dump(credentials, f, indent=2)
                        with contextlib.suppress(OSError, AttributeError):
                            # chmod may fail on Windows or some filesystems
                            self.config_file.chmod(0o600)
                    else:
                        # No credentials left, remove files
                        self.config_file.unlink()
                        if self.key_file.exists():
                            self.key_file.unlink()
                        salt_file = self.config_dir / ".salt"
                        if salt_file.exists():
                            salt_file.unlink()
            except (OSError, json.JSONDecodeError):
                # File operation error - safe to ignore during cleanup
                pass

    def get_active_server(self) -> Optional[str]:
        """Get the most recently used server"""
        servers = self.list_servers()
        return servers[-1] if servers else None
