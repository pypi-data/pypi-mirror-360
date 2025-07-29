"""Secure credential management for Pi-hole MCP server."""

import getpass
import json
import os
import socket
import stat
from base64 import b64decode, b64encode
from dataclasses import asdict, dataclass
from pathlib import Path

import keyring
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from keyring.errors import KeyringError

from .pihole_client import PiHoleConfig


@dataclass
class StoredCredentials:
    """Stored Pi-hole credentials."""

    host: str
    port: int
    api_key: str = ""
    web_password: str = ""
    use_https: bool = False
    verify_ssl: bool = True
    timeout: int = 30
    api_version: str | None = None

    def to_pihole_config(self) -> PiHoleConfig:
        """Convert to PiHoleConfig."""
        return PiHoleConfig(
            host=self.host,
            port=self.port,
            api_key=self.api_key if self.api_key else None,
            web_password=self.web_password if self.web_password else None,
            use_https=self.use_https,
            verify_ssl=self.verify_ssl,
            timeout=self.timeout,
            api_version=self.api_version,
        )

    @classmethod
    def from_pihole_config(cls, config: PiHoleConfig) -> "StoredCredentials":
        """Create from PiHoleConfig."""
        return cls(
            host=config.host,
            port=config.port,
            api_key=config.api_key or "",
            web_password=config.web_password or "",
            use_https=config.use_https,
            verify_ssl=config.verify_ssl,
            timeout=config.timeout,
            api_version=config.api_version,
        )


class CredentialError(Exception):
    """Base exception for credential errors."""

    pass


class CredentialNotFoundError(CredentialError):
    """Exception raised when credentials are not found."""

    pass


class CredentialStorageError(CredentialError):
    """Exception raised when credential storage fails."""

    pass


class CredentialDecryptionError(CredentialError):
    """Exception raised when credential decryption fails."""

    pass


class CredentialManager:
    """Secure credential manager for Pi-hole credentials."""

    def __init__(self, config_dir: Path | None = None) -> None:
        """Initialize credential manager.

        Args:
            config_dir: Configuration directory (default: ~/.local/share/pihole-mcp-server)
        """
        if config_dir is None:
            config_dir = Path.home() / ".local" / "share" / "pihole-mcp-server"

        self.config_dir = config_dir
        self.config_file = config_dir / "credentials.json"
        self.keyring_service = "pihole-mcp-server"

        # Ensure config directory exists with proper permissions
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists with proper permissions."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Set restrictive permissions (owner only)
        try:
            self.config_dir.chmod(stat.S_IRWXU)  # 700
        except OSError:
            # May fail on some systems, but not critical
            pass

    def _derive_key(self, password: bytes, salt: bytes) -> bytes:
        """Derive encryption key from password and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return b64encode(kdf.derive(password))

    def _encrypt_data(self, data: str, password: str) -> dict[str, str]:
        """Encrypt data with password.

        Args:
            data: Data to encrypt
            password: Password for encryption

        Returns:
            Dictionary with encrypted data and salt
        """
        salt = os.urandom(16)
        key = self._derive_key(password.encode(), salt)
        f = Fernet(key)

        encrypted_data = f.encrypt(data.encode())

        return {
            "encrypted_data": b64encode(encrypted_data).decode(),
            "salt": b64encode(salt).decode(),
        }

    def _decrypt_data(self, encrypted_data: str, salt: str, password: str) -> str:
        """Decrypt data with password.

        Args:
            encrypted_data: Encrypted data
            salt: Salt used for encryption
            password: Password for decryption

        Returns:
            Decrypted data

        Raises:
            CredentialDecryptionError: If decryption fails
        """
        try:
            salt_bytes = b64decode(salt.encode())
            key = self._derive_key(password.encode(), salt_bytes)
            f = Fernet(key)

            encrypted_bytes = b64decode(encrypted_data.encode())
            decrypted_data = f.decrypt(encrypted_bytes)

            return decrypted_data.decode()
        except (InvalidToken, ValueError, UnicodeDecodeError) as e:
            raise CredentialDecryptionError(f"Failed to decrypt data: {e}")

    def _get_machine_id(self) -> str:
        """Get a machine-specific identifier for encryption."""
        # Try to get a machine-specific ID
        machine_id = None

        # Try /etc/machine-id (Linux)
        if os.path.exists("/etc/machine-id"):
            try:
                with open("/etc/machine-id") as f:
                    machine_id = f.read().strip()
            except OSError:
                pass

        # Try /var/lib/dbus/machine-id (Linux)
        if not machine_id and os.path.exists("/var/lib/dbus/machine-id"):
            try:
                with open("/var/lib/dbus/machine-id") as f:
                    machine_id = f.read().strip()
            except OSError:
                pass

        # Fallback to hostname + username
        if not machine_id:
            machine_id = f"{socket.gethostname()}-{getpass.getuser()}"

        return machine_id

    def _try_keyring_storage(self, credentials: StoredCredentials) -> bool:
        """Try to store credentials in keyring.

        Args:
            credentials: Credentials to store

        Returns:
            True if successful
        """
        try:
            data = json.dumps(asdict(credentials))
            keyring.set_password(self.keyring_service, "default", data)
            return True
        except KeyringError:
            return False

    def _try_keyring_retrieval(self) -> StoredCredentials | None:
        """Try to retrieve credentials from keyring.

        Returns:
            Stored credentials or None if not found
        """
        try:
            data = keyring.get_password(self.keyring_service, "default")
            if data:
                cred_dict = json.loads(data)
                return StoredCredentials(**cred_dict)
        except (KeyringError, json.JSONDecodeError, TypeError):
            pass
        return None

    def _try_keyring_deletion(self) -> bool:
        """Try to delete credentials from keyring.

        Returns:
            True if successful
        """
        try:
            keyring.delete_password(self.keyring_service, "default")
            return True
        except KeyringError:
            return False

    def _store_file_credentials(self, credentials: StoredCredentials) -> None:
        """Store credentials in encrypted file.

        Args:
            credentials: Credentials to store

        Raises:
            CredentialStorageError: If storage fails
        """
        try:
            data = json.dumps(asdict(credentials))
            password = self._get_machine_id()
            encrypted = self._encrypt_data(data, password)

            with open(self.config_file, "w") as f:
                json.dump(encrypted, f)

            # Set restrictive permissions
            self.config_file.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600

        except (OSError, json.JSONDecodeError) as e:
            raise CredentialStorageError(f"Failed to store credentials: {e}")

    def _load_file_credentials(self) -> StoredCredentials | None:
        """Load credentials from encrypted file.

        Returns:
            Stored credentials or None if not found

        Raises:
            CredentialDecryptionError: If decryption fails
        """
        if not self.config_file.exists():
            return None

        try:
            with open(self.config_file) as f:
                encrypted = json.load(f)

            password = self._get_machine_id()
            data = self._decrypt_data(
                encrypted["encrypted_data"], encrypted["salt"], password
            )

            cred_dict = json.loads(data)
            return StoredCredentials(**cred_dict)

        except (OSError, json.JSONDecodeError, KeyError, TypeError) as e:
            raise CredentialDecryptionError(f"Failed to load credentials: {e}")

    def _delete_file_credentials(self) -> bool:
        """Delete credentials file.

        Returns:
            True if successful
        """
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            return True
        except OSError:
            return False

    def store_credentials(self, credentials: StoredCredentials) -> None:
        """Store Pi-hole credentials securely.

        Args:
            credentials: Credentials to store

        Raises:
            CredentialStorageError: If storage fails
        """
        # Try keyring first (most secure)
        if self._try_keyring_storage(credentials):
            return

        # Fallback to encrypted file
        self._store_file_credentials(credentials)

    def load_credentials(self) -> StoredCredentials:
        """Load Pi-hole credentials.

        Returns:
            Stored credentials

        Raises:
            CredentialNotFoundError: If credentials not found
            CredentialDecryptionError: If decryption fails
        """
        # Try keyring first
        credentials = self._try_keyring_retrieval()
        if credentials:
            return credentials

        # Try encrypted file
        credentials = self._load_file_credentials()
        if credentials:
            return credentials

        raise CredentialNotFoundError("No Pi-hole credentials found")

    def delete_credentials(self) -> None:
        """Delete stored Pi-hole credentials."""
        # Try to delete from keyring
        self._try_keyring_deletion()

        # Try to delete file
        self._delete_file_credentials()

    def has_credentials(self) -> bool:
        """Check if credentials are stored.

        Returns:
            True if credentials exist
        """
        try:
            self.load_credentials()
            return True
        except CredentialNotFoundError:
            return False

    def get_pihole_config(self) -> PiHoleConfig:
        """Get Pi-hole configuration from stored credentials.

        Returns:
            Pi-hole configuration

        Raises:
            CredentialNotFoundError: If credentials not found
            CredentialDecryptionError: If decryption fails
        """
        credentials = self.load_credentials()
        return credentials.to_pihole_config()

    def store_pihole_config(self, config: PiHoleConfig) -> None:
        """Store Pi-hole configuration as credentials.

        Args:
            config: Pi-hole configuration

        Raises:
            CredentialStorageError: If storage fails
        """
        if not config.api_key and not config.web_password:
            raise CredentialStorageError("Either API key or web password is required")

        credentials = StoredCredentials.from_pihole_config(config)
        self.store_credentials(credentials)
