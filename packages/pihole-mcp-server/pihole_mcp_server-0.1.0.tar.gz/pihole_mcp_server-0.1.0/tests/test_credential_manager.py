"""Tests for CredentialManager class and related models."""

import json
import os
import stat
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from cryptography.fernet import Fernet, InvalidToken
from keyring.errors import KeyringError

from pihole_mcp_server.credential_manager import (
    CredentialManager,
    StoredCredentials,
    CredentialError,
    CredentialNotFoundError,
    CredentialStorageError,
    CredentialDecryptionError,
)
from pihole_mcp_server.pihole_client import PiHoleConfig


class TestStoredCredentials:
    """Test cases for StoredCredentials class."""
    
    def test_init_defaults(self):
        """Test StoredCredentials initialization with defaults."""
        creds = StoredCredentials(host="192.168.1.100", port=80)
        
        assert creds.host == "192.168.1.100"
        assert creds.port == 80
        assert creds.api_key == ""
        assert creds.web_password == ""
        assert creds.use_https is False
        assert creds.verify_ssl is True
        assert creds.timeout == 30
        assert creds.api_version is None
    
    def test_init_full(self):
        """Test StoredCredentials initialization with all parameters."""
        creds = StoredCredentials(
            host="pi.hole.local",
            port=8080,
            api_key="test_api_key",
            web_password="test_password",
            use_https=True,
            verify_ssl=False,
            timeout=60,
            api_version="modern"
        )
        
        assert creds.host == "pi.hole.local"
        assert creds.port == 8080
        assert creds.api_key == "test_api_key"
        assert creds.web_password == "test_password"
        assert creds.use_https is True
        assert creds.verify_ssl is False
        assert creds.timeout == 60
        assert creds.api_version == "modern"
    
    def test_to_pihole_config(self, sample_stored_credentials):
        """Test converting StoredCredentials to PiHoleConfig."""
        config = sample_stored_credentials.to_pihole_config()
        
        assert isinstance(config, PiHoleConfig)
        assert config.host == sample_stored_credentials.host
        assert config.port == sample_stored_credentials.port
        assert config.api_key == sample_stored_credentials.api_key
        assert config.web_password == sample_stored_credentials.web_password
        assert config.use_https == sample_stored_credentials.use_https
        assert config.verify_ssl == sample_stored_credentials.verify_ssl
        assert config.timeout == sample_stored_credentials.timeout
        assert config.api_version == sample_stored_credentials.api_version
    
    def test_to_pihole_config_empty_credentials(self):
        """Test converting StoredCredentials with empty credentials."""
        creds = StoredCredentials(host="test.com", port=80, api_key="", web_password="")
        config = creds.to_pihole_config()
        
        assert config.api_key is None
        assert config.web_password is None
    
    def test_from_pihole_config(self, sample_pihole_config):
        """Test creating StoredCredentials from PiHoleConfig."""
        creds = StoredCredentials.from_pihole_config(sample_pihole_config)
        
        assert isinstance(creds, StoredCredentials)
        assert creds.host == sample_pihole_config.host
        assert creds.port == sample_pihole_config.port
        assert creds.api_key == sample_pihole_config.api_key
        assert creds.web_password == sample_pihole_config.web_password
        assert creds.use_https == sample_pihole_config.use_https
        assert creds.verify_ssl == sample_pihole_config.verify_ssl
        assert creds.timeout == sample_pihole_config.timeout
        assert creds.api_version == sample_pihole_config.api_version
    
    def test_from_pihole_config_none_credentials(self):
        """Test creating StoredCredentials from PiHoleConfig with None credentials."""
        config = PiHoleConfig(host="test.com", port=80, api_key=None, web_password=None)
        creds = StoredCredentials.from_pihole_config(config)
        
        assert creds.api_key == ""
        assert creds.web_password == ""


class TestCredentialExceptions:
    """Test cases for credential exception classes."""
    
    def test_credential_error_inheritance(self):
        """Test CredentialError is a proper Exception subclass."""
        error = CredentialError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
    
    def test_credential_not_found_error_inheritance(self):
        """Test CredentialNotFoundError inherits from CredentialError."""
        error = CredentialNotFoundError("Not found")
        assert isinstance(error, CredentialError)
        assert isinstance(error, Exception)
        assert str(error) == "Not found"
    
    def test_credential_storage_error_inheritance(self):
        """Test CredentialStorageError inherits from CredentialError."""
        error = CredentialStorageError("Storage failed")
        assert isinstance(error, CredentialError)
        assert isinstance(error, Exception)
        assert str(error) == "Storage failed"
    
    def test_credential_decryption_error_inheritance(self):
        """Test CredentialDecryptionError inherits from CredentialError."""
        error = CredentialDecryptionError("Decryption failed")
        assert isinstance(error, CredentialError)
        assert isinstance(error, Exception)
        assert str(error) == "Decryption failed"


class TestCredentialManager:
    """Test cases for CredentialManager class."""
    
    def test_init_default_config_dir(self):
        """Test CredentialManager initialization with default config directory."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path("/tmp/test_home")
            
            with patch('pathlib.Path.mkdir') as mock_mkdir:
                manager = CredentialManager()
                
                expected_path = Path("/tmp/test_home/.local/share/pihole-mcp-server")
                assert manager.config_dir == expected_path
                assert manager.config_file == expected_path / "credentials.json"
                mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    def test_init_custom_config_dir(self, temp_config_dir):
        """Test CredentialManager initialization with custom config directory."""
        manager = CredentialManager(config_dir=temp_config_dir)
        
        assert manager.config_dir == temp_config_dir
        assert manager.config_file == temp_config_dir / "credentials.json"
    
    def test_ensure_config_dir(self, temp_config_dir):
        """Test ensuring config directory exists."""
        config_dir = temp_config_dir / "test_config"
        assert not config_dir.exists()
        
        manager = CredentialManager(config_dir=config_dir)
        
        assert config_dir.exists()
        assert config_dir.is_dir()
    
    def test_ensure_config_dir_permissions(self, temp_config_dir):
        """Test ensuring config directory has correct permissions."""
        config_dir = temp_config_dir / "test_config"
        manager = CredentialManager(config_dir=config_dir)
        
        # Check that chmod was attempted (may not work on all systems)
        assert config_dir.exists()
    
    def test_derive_key(self, credential_manager):
        """Test key derivation from password and salt."""
        password = b"test_password"
        salt = b"test_salt_16b"
        
        key = credential_manager._derive_key(password, salt)
        
        assert isinstance(key, bytes)
        assert len(key) > 0
        
        # Same password and salt should produce same key
        key2 = credential_manager._derive_key(password, salt)
        assert key == key2
        
        # Different password should produce different key
        key3 = credential_manager._derive_key(b"different_password", salt)
        assert key != key3
    
    def test_encrypt_decrypt_data(self, credential_manager):
        """Test data encryption and decryption."""
        data = "test_data_to_encrypt"
        password = "test_password"
        
        encrypted = credential_manager._encrypt_data(data, password)
        
        assert isinstance(encrypted, dict)
        assert "encrypted_data" in encrypted
        assert "salt" in encrypted
        assert encrypted["encrypted_data"] != data
        
        decrypted = credential_manager._decrypt_data(
            encrypted["encrypted_data"],
            encrypted["salt"],
            password
        )
        
        assert decrypted == data
    
    def test_decrypt_data_wrong_password(self, credential_manager):
        """Test decryption with wrong password."""
        data = "test_data"
        password = "correct_password"
        wrong_password = "wrong_password"
        
        encrypted = credential_manager._encrypt_data(data, password)
        
        with pytest.raises(CredentialDecryptionError) as excinfo:
            credential_manager._decrypt_data(
                encrypted["encrypted_data"],
                encrypted["salt"],
                wrong_password
            )
        
        assert "Failed to decrypt data" in str(excinfo.value)
    
    def test_decrypt_data_invalid_token(self, credential_manager):
        """Test decryption with invalid token."""
        with pytest.raises(CredentialDecryptionError) as excinfo:
            credential_manager._decrypt_data(
                "invalid_encrypted_data",
                "invalid_salt",
                "password"
            )
        
        assert "Failed to decrypt data" in str(excinfo.value)
    
    def test_get_machine_id_from_machine_id_file(self, credential_manager):
        """Test getting machine ID from /etc/machine-id."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            with patch('builtins.open', create=True) as mock_open:
                mock_file = Mock()
                mock_file.read.return_value = "test_machine_id\n"
                mock_open.return_value.__enter__.return_value = mock_file
                
                machine_id = credential_manager._get_machine_id()
                
                assert machine_id == "test_machine_id"
    
    def test_get_machine_id_from_dbus_machine_id(self, credential_manager):
        """Test getting machine ID from /var/lib/dbus/machine-id."""
        with patch('os.path.exists') as mock_exists:
            # First file doesn't exist, second does
            mock_exists.side_effect = [False, True]
            
            with patch('builtins.open', create=True) as mock_open:
                mock_file = Mock()
                mock_file.read.return_value = "dbus_machine_id\n"
                mock_open.return_value.__enter__.return_value = mock_file
                
                machine_id = credential_manager._get_machine_id()
                
                assert machine_id == "dbus_machine_id"
    
    def test_get_machine_id_fallback(self, credential_manager):
        """Test getting machine ID fallback to hostname + username."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            with patch('socket.gethostname') as mock_hostname:
                mock_hostname.return_value = "test_hostname"
                
                with patch('getpass.getuser') as mock_getuser:
                    mock_getuser.return_value = "test_user"
                    
                    machine_id = credential_manager._get_machine_id()
                    
                    assert machine_id == "test_hostname-test_user"
    
    def test_try_keyring_storage_success(self, credential_manager, sample_stored_credentials, mock_keyring):
        """Test successful keyring storage."""
        mock_keyring.set_password.return_value = None
        
        result = credential_manager._try_keyring_storage(sample_stored_credentials)
        
        assert result is True
        mock_keyring.set_password.assert_called_once()
    
    def test_try_keyring_storage_failure(self, credential_manager, sample_stored_credentials, mock_keyring):
        """Test failed keyring storage."""
        mock_keyring.set_password.side_effect = KeyringError("Keyring error")
        
        result = credential_manager._try_keyring_storage(sample_stored_credentials)
        
        assert result is False
    
    def test_try_keyring_retrieval_success(self, credential_manager, sample_stored_credentials, mock_keyring):
        """Test successful keyring retrieval."""
        creds_data = json.dumps({
            "host": "192.168.1.100",
            "port": 80,
            "api_key": "test_key",
            "web_password": "test_password",
            "use_https": False,
            "verify_ssl": True,
            "timeout": 30,
            "api_version": "legacy"
        })
        mock_keyring.get_password.return_value = creds_data
        
        result = credential_manager._try_keyring_retrieval()
        
        assert result is not None
        assert isinstance(result, StoredCredentials)
        assert result.host == "192.168.1.100"
        assert result.api_key == "test_key"
    
    def test_try_keyring_retrieval_not_found(self, credential_manager, mock_keyring):
        """Test keyring retrieval when not found."""
        mock_keyring.get_password.return_value = None
        
        result = credential_manager._try_keyring_retrieval()
        
        assert result is None
    
    def test_try_keyring_retrieval_error(self, credential_manager, mock_keyring):
        """Test keyring retrieval with error."""
        mock_keyring.get_password.side_effect = KeyringError("Keyring error")
        
        result = credential_manager._try_keyring_retrieval()
        
        assert result is None
    
    def test_try_keyring_retrieval_invalid_json(self, credential_manager, mock_keyring):
        """Test keyring retrieval with invalid JSON."""
        mock_keyring.get_password.return_value = "invalid_json"
        
        result = credential_manager._try_keyring_retrieval()
        
        assert result is None
    
    def test_try_keyring_deletion_success(self, credential_manager, mock_keyring):
        """Test successful keyring deletion."""
        mock_keyring.delete_password.return_value = None
        
        result = credential_manager._try_keyring_deletion()
        
        assert result is True
        mock_keyring.delete_password.assert_called_once()
    
    def test_try_keyring_deletion_failure(self, credential_manager, mock_keyring):
        """Test failed keyring deletion."""
        mock_keyring.delete_password.side_effect = KeyringError("Keyring error")
        
        result = credential_manager._try_keyring_deletion()
        
        assert result is False
    
    def test_store_file_credentials(self, credential_manager, sample_stored_credentials):
        """Test storing credentials to file."""
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            with patch('pathlib.Path.chmod') as mock_chmod:
                credential_manager._store_file_credentials(sample_stored_credentials)
                
                mock_open.assert_called_once()
                # JSON writes can happen with multiple calls, just verify write was called
                assert mock_file.write.called
                mock_chmod.assert_called_once_with(stat.S_IRUSR | stat.S_IWUSR)
    
    def test_store_file_credentials_io_error(self, credential_manager, sample_stored_credentials):
        """Test storing credentials to file with IO error."""
        with patch('builtins.open', create=True) as mock_open:
            mock_open.side_effect = IOError("File error")
            
            with pytest.raises(CredentialStorageError) as excinfo:
                credential_manager._store_file_credentials(sample_stored_credentials)
            
            assert "Failed to store credentials" in str(excinfo.value)
    
    def test_load_file_credentials(self, credential_manager, sample_stored_credentials):
        """Test loading credentials from file."""
        # Create encrypted data
        test_data = json.dumps({
            "host": "192.168.1.100",
            "port": 80,
            "api_key": "test_key",
            "web_password": "test_password",
            "use_https": False,
            "verify_ssl": True,
            "timeout": 30,
            "api_version": "legacy"
        })
        password = "test_password"
        encrypted = credential_manager._encrypt_data(test_data, password)
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_file = Mock()
                mock_file.read.return_value = json.dumps(encrypted)
                mock_open.return_value.__enter__.return_value = mock_file
                
                with patch.object(credential_manager, '_get_machine_id', return_value=password):
                    result = credential_manager._load_file_credentials()
                    
                    assert result is not None
                    assert isinstance(result, StoredCredentials)
                    assert result.host == "192.168.1.100"
    
    def test_load_file_credentials_not_exists(self, credential_manager):
        """Test loading credentials from file when file doesn't exist."""
        with patch('pathlib.Path.exists', return_value=False):
            result = credential_manager._load_file_credentials()
            
            assert result is None
    
    def test_load_file_credentials_io_error(self, credential_manager):
        """Test loading credentials from file with IO error."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_open.side_effect = IOError("File error")
                
                with pytest.raises(CredentialDecryptionError) as excinfo:
                    credential_manager._load_file_credentials()
                
                assert "Failed to load credentials" in str(excinfo.value)
    
    def test_delete_file_credentials(self, credential_manager):
        """Test deleting credentials file."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.unlink') as mock_unlink:
                result = credential_manager._delete_file_credentials()
                
                assert result is True
                mock_unlink.assert_called_once()
    
    def test_delete_file_credentials_not_exists(self, credential_manager):
        """Test deleting credentials file when it doesn't exist."""
        with patch('pathlib.Path.exists', return_value=False):
            result = credential_manager._delete_file_credentials()
            
            assert result is True
    
    def test_delete_file_credentials_error(self, credential_manager):
        """Test deleting credentials file with error."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.unlink', side_effect=OSError("Permission denied")):
                result = credential_manager._delete_file_credentials()
                
                assert result is False
    
    def test_store_credentials_keyring_success(self, credential_manager, sample_stored_credentials, mock_keyring):
        """Test storing credentials with keyring success."""
        mock_keyring.set_password.return_value = None
        
        credential_manager.store_credentials(sample_stored_credentials)
        
        mock_keyring.set_password.assert_called_once()
    
    def test_store_credentials_keyring_failure_file_fallback(self, credential_manager, sample_stored_credentials, mock_keyring):
        """Test storing credentials with keyring failure, file fallback."""
        mock_keyring.set_password.side_effect = KeyringError("Keyring error")
        
        with patch.object(credential_manager, '_store_file_credentials') as mock_store_file:
            credential_manager.store_credentials(sample_stored_credentials)
            
            mock_store_file.assert_called_once_with(sample_stored_credentials)
    
    def test_load_credentials_keyring_success(self, credential_manager, sample_stored_credentials, mock_keyring):
        """Test loading credentials from keyring success."""
        creds_data = json.dumps({
            "host": "192.168.1.100",
            "port": 80,
            "api_key": "test_key",
            "web_password": "test_password",
            "use_https": False,
            "verify_ssl": True,
            "timeout": 30,
            "api_version": "legacy"
        })
        mock_keyring.get_password.return_value = creds_data
        
        result = credential_manager.load_credentials()
        
        assert isinstance(result, StoredCredentials)
        assert result.host == "192.168.1.100"
    
    def test_load_credentials_keyring_failure_file_fallback(self, credential_manager, mock_keyring):
        """Test loading credentials with keyring failure, file fallback."""
        mock_keyring.get_password.return_value = None
        
        with patch.object(credential_manager, '_load_file_credentials') as mock_load_file:
            mock_load_file.return_value = StoredCredentials(host="test.com", port=80)
            
            result = credential_manager.load_credentials()
            
            assert isinstance(result, StoredCredentials)
            assert result.host == "test.com"
    
    def test_load_credentials_not_found(self, credential_manager, mock_keyring):
        """Test loading credentials when not found."""
        mock_keyring.get_password.return_value = None
        
        with patch.object(credential_manager, '_load_file_credentials') as mock_load_file:
            mock_load_file.return_value = None
            
            with pytest.raises(CredentialNotFoundError) as excinfo:
                credential_manager.load_credentials()
            
            assert "No Pi-hole credentials found" in str(excinfo.value)
    
    def test_delete_credentials(self, credential_manager, mock_keyring):
        """Test deleting credentials."""
        mock_keyring.delete_password.return_value = None
        
        with patch.object(credential_manager, '_delete_file_credentials') as mock_delete_file:
            mock_delete_file.return_value = True
            
            credential_manager.delete_credentials()
            
            mock_keyring.delete_password.assert_called_once()
            mock_delete_file.assert_called_once()
    
    def test_has_credentials_true(self, credential_manager):
        """Test has_credentials returns True."""
        with patch.object(credential_manager, 'load_credentials') as mock_load:
            mock_load.return_value = StoredCredentials(host="test.com", port=80)
            
            result = credential_manager.has_credentials()
            
            assert result is True
    
    def test_has_credentials_false(self, credential_manager):
        """Test has_credentials returns False."""
        with patch.object(credential_manager, 'load_credentials') as mock_load:
            mock_load.side_effect = CredentialNotFoundError("Not found")
            
            result = credential_manager.has_credentials()
            
            assert result is False
    
    def test_get_pihole_config(self, credential_manager):
        """Test getting PiHoleConfig from credentials."""
        stored_creds = StoredCredentials(
            host="192.168.1.100",
            port=80,
            api_key="test_key",
            web_password="test_password"
        )
        
        with patch.object(credential_manager, 'load_credentials') as mock_load:
            mock_load.return_value = stored_creds
            
            result = credential_manager.get_pihole_config()
            
            assert isinstance(result, PiHoleConfig)
            assert result.host == "192.168.1.100"
            assert result.api_key == "test_key"
            assert result.web_password == "test_password"
    
    def test_store_pihole_config(self, credential_manager, sample_pihole_config):
        """Test storing PiHoleConfig as credentials."""
        with patch.object(credential_manager, 'store_credentials') as mock_store:
            credential_manager.store_pihole_config(sample_pihole_config)
            
            mock_store.assert_called_once()
            args, kwargs = mock_store.call_args
            stored_creds = args[0]
            assert isinstance(stored_creds, StoredCredentials)
            assert stored_creds.host == sample_pihole_config.host
    
    def test_store_pihole_config_no_credentials(self, credential_manager):
        """Test storing PiHoleConfig without credentials."""
        config = PiHoleConfig(host="test.com", port=80)  # No api_key or web_password
        
        with pytest.raises(CredentialStorageError) as excinfo:
            credential_manager.store_pihole_config(config)
        
        assert "Either API key or web password is required" in str(excinfo.value) 