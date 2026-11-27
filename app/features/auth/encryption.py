"""Cifrado en reposo del secreto TOTP (User.totp_secret).

Con el secreto TOTP en claro, quien obtenga una copia de la base de datos puede
generar los códigos de cualquier usuario y el segundo factor deja de servir. Por
eso la columna guarda un token Fernet (AES-128-CBC + HMAC-SHA256) y el modelo
trabaja con el valor en claro: se cifra al escribir y se descifra al leer.

Clave (en este orden):

1. ``TOTP_ENCRYPTION_KEY``: una o varias claves Fernet separadas por comas. La
   primera cifra y todas descifran, así que para rotar se pone la nueva delante
   y se deja la antigua detrás hasta que no quede ningún secreto cifrado con
   ella. Se genera con::

       python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

2. Una clave derivada de ``SECRET_KEY`` con HKDF. Siempre se usa para descifrar
   y, si no hay ``TOTP_ENCRYPTION_KEY``, también para cifrar. Así la aplicación
   funciona sin configurar nada más y el secreto sigue protegido frente a una
   filtración de solo la base de datos. Ojo: cambiar ``SECRET_KEY`` sin haber
   definido ``TOTP_ENCRYPTION_KEY`` deja ilegibles los secretos existentes.

El valor se busca primero en ``app.config`` y después en las variables de
entorno, de modo que los tests pueden fijarlo en la configuración.
"""

import base64
import logging
import os

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from flask import current_app
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

logger = logging.getLogger(__name__)

ENCRYPTION_KEY_SETTING = "TOTP_ENCRYPTION_KEY"
# Separa esta clave de cualquier otro uso de SECRET_KEY (sesiones, CSRF...).
_HKDF_INFO = b"uvlhub:auth:totp_secret:v1"


class TOTPEncryptionConfigError(RuntimeError):
    """La clave configurada en TOTP_ENCRYPTION_KEY no es una clave Fernet válida."""


def _setting(name: str) -> str | None:
    value = current_app.config.get(name) or os.getenv(name)
    return value.strip() if isinstance(value, str) and value.strip() else None


def _key_derived_from_secret_key() -> bytes | None:
    secret_key = current_app.config.get("SECRET_KEY")
    if not secret_key:
        return None
    if isinstance(secret_key, str):
        secret_key = secret_key.encode()
    derived = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=_HKDF_INFO).derive(secret_key)
    return base64.urlsafe_b64encode(derived)


def _explicit_keys() -> list[bytes]:
    raw = _setting(ENCRYPTION_KEY_SETTING)
    if not raw:
        return []
    return [key.strip().encode() for key in raw.split(",") if key.strip()]


def _fernet() -> MultiFernet:
    keys = _explicit_keys()
    derived = _key_derived_from_secret_key()
    if derived is not None:
        keys.append(derived)
    if not keys:
        raise TOTPEncryptionConfigError(f"Cannot encrypt TOTP secrets: set {ENCRYPTION_KEY_SETTING} or SECRET_KEY.")
    try:
        return MultiFernet([Fernet(key) for key in keys])
    except (ValueError, TypeError) as exc:
        raise TOTPEncryptionConfigError(
            f"{ENCRYPTION_KEY_SETTING} must contain url-safe base64 Fernet keys (32 bytes), " "separated by commas."
        ) from exc


def encrypt_secret(plain: str) -> str:
    return _fernet().encrypt(plain.encode()).decode()


def decrypt_secret(token: str) -> str | None:
    """Devuelve el secreto en claro, o None si no se puede descifrar.

    No se lanza la excepción porque se descifra al cargar el usuario: un error
    aquí rompería cualquier petición de ese usuario, incluido el login. Con
    None, verify_totp devuelve False y el usuario aún puede entrar con un
    código de recuperación mientras se corrige la clave.
    """
    try:
        return _fernet().decrypt(token.encode()).decode()
    except InvalidToken:
        logger.error(
            "Could not decrypt a stored TOTP secret: the encryption key changed or the value "
            "was not encrypted. Check %s and SECRET_KEY.",
            ENCRYPTION_KEY_SETTING,
        )
        return None


class EncryptedString(TypeDecorator):
    """Cadena que se guarda cifrada con Fernet y se lee en claro.

    El cifrado no es determinista (cada escritura da un token distinto), así
    que no sirve para filtrar ni comparar en SQL: solo para guardar y leer.
    Un token ocupa unos 140 caracteres para un secreto base32 de 32.
    """

    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return encrypt_secret(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return decrypt_secret(value)
