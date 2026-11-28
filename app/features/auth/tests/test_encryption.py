"""Unit tests for the TOTP secret encryption — no database.

The key is read from the Flask config, so each test pushes a bare ``Flask``
app context with the settings it needs (not the project's app).
"""

import pytest
from cryptography.fernet import Fernet
from flask import Flask

from app.features.auth.encryption import (
    ENCRYPTION_KEY_SETTING,
    EncryptedString,
    TOTPEncryptionConfigError,
    decrypt_secret,
    encrypt_secret,
)

pytestmark = pytest.mark.unit

SECRET = "JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP"


@pytest.fixture(autouse=True)
def _no_key_in_environment(monkeypatch):
    # Que una TOTP_ENCRYPTION_KEY del entorno de quien ejecuta no cambie los resultados.
    monkeypatch.delenv(ENCRYPTION_KEY_SETTING, raising=False)


def _context(**config):
    app = Flask(__name__)
    app.config.update(config)
    return app.app_context()


def test_encrypted_value_is_not_the_secret_and_round_trips():
    with _context(SECRET_KEY="test-secret-key"):
        token = encrypt_secret(SECRET)
        assert SECRET not in token
        assert decrypt_secret(token) == SECRET


def test_encryption_is_not_deterministic():
    with _context(SECRET_KEY="test-secret-key"):
        assert encrypt_secret(SECRET) != encrypt_secret(SECRET)


def test_token_fits_the_column():
    with _context(SECRET_KEY="test-secret-key"):
        assert len(encrypt_secret(SECRET)) <= 255


def test_explicit_key_is_used_instead_of_secret_key():
    key = Fernet.generate_key().decode()
    with _context(SECRET_KEY="test-secret-key", TOTP_ENCRYPTION_KEY=key):
        token = encrypt_secret(SECRET)
    assert Fernet(key).decrypt(token.encode()).decode() == SECRET


def test_key_from_environment_is_used(monkeypatch):
    key = Fernet.generate_key().decode()
    monkeypatch.setenv(ENCRYPTION_KEY_SETTING, key)
    with _context(SECRET_KEY="test-secret-key"):
        token = encrypt_secret(SECRET)
    assert Fernet(key).decrypt(token.encode()).decode() == SECRET


def test_key_rotation_keeps_old_secrets_readable():
    old_key = Fernet.generate_key().decode()
    new_key = Fernet.generate_key().decode()
    with _context(SECRET_KEY="test-secret-key", TOTP_ENCRYPTION_KEY=old_key):
        old_token = encrypt_secret(SECRET)
    with _context(SECRET_KEY="test-secret-key", TOTP_ENCRYPTION_KEY=f"{new_key}, {old_key}"):
        assert decrypt_secret(old_token) == SECRET
        new_token = encrypt_secret(SECRET)
    assert Fernet(new_key).decrypt(new_token.encode()).decode() == SECRET


def test_secrets_encrypted_with_secret_key_stay_readable_after_adding_explicit_key():
    with _context(SECRET_KEY="test-secret-key"):
        token = encrypt_secret(SECRET)
    with _context(SECRET_KEY="test-secret-key", TOTP_ENCRYPTION_KEY=Fernet.generate_key().decode()):
        assert decrypt_secret(token) == SECRET


def test_other_secret_key_cannot_decrypt(caplog):
    with _context(SECRET_KEY="test-secret-key"):
        token = encrypt_secret(SECRET)
    with _context(SECRET_KEY="another-secret-key"):
        assert decrypt_secret(token) is None
    assert "Could not decrypt a stored TOTP secret" in caplog.text


def test_plaintext_value_is_not_returned_as_secret():
    with _context(SECRET_KEY="test-secret-key"):
        assert decrypt_secret(SECRET) is None


def test_invalid_explicit_key_raises_config_error():
    with _context(SECRET_KEY="test-secret-key", TOTP_ENCRYPTION_KEY="<CHANGE_THIS>"):
        with pytest.raises(TOTPEncryptionConfigError):
            encrypt_secret(SECRET)


def test_missing_keys_raise_config_error():
    with _context(SECRET_KEY=None):
        with pytest.raises(TOTPEncryptionConfigError):
            encrypt_secret(SECRET)


def test_encrypted_string_type_passes_none_through():
    column_type = EncryptedString(255)
    assert column_type.process_bind_param(None, None) is None
    assert column_type.process_result_value(None, None) is None


def test_encrypted_string_type_round_trips():
    column_type = EncryptedString(255)
    with _context(SECRET_KEY="test-secret-key"):
        stored = column_type.process_bind_param(SECRET, None)
        assert stored != SECRET
        assert column_type.process_result_value(stored, None) == SECRET
