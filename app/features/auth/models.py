import hashlib
import hmac
import secrets
from datetime import datetime, timezone

import pyotp
from flask_login import UserMixin
from sqlalchemy import false
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.features.auth.encryption import EncryptedString

# Nombre que muestran las apps de autenticación (Google Authenticator, Authy...).
TOTP_ISSUER = "Esports-hub"
# Códigos válidos un paso antes y uno después del actual (±30 s) por desfase de reloj.
TOTP_VALID_WINDOW = 1

RECOVERY_CODE_COUNT = 10
# 16 caracteres de un alfabeto de 31 son ~79 bits aleatorios: con esa entropía
# basta un SHA-256 (no hace falta un hash lento como el de las contraseñas, que
# tarda ~0,7 s por comprobación) y el código se puede buscar por su hash.
RECOVERY_CODE_LENGTH = 16
RECOVERY_CODE_GROUP = 4
# Sin caracteres que se confunden al copiarlos a mano (0/o, 1/l/i).
RECOVERY_CODE_ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Secreto TOTP en base32. Se genera al empezar a configurar el 2FA y solo
    # cuenta cuando two_factor_enabled es True (tras confirmar un primer código).
    # En la base de datos se guarda cifrado (ver encryption.py); el atributo
    # siempre tiene el valor en claro.
    totp_secret = db.Column(EncryptedString(255), nullable=True)
    two_factor_enabled = db.Column(db.Boolean, nullable=False, default=False, server_default=false())

    data_sets = db.relationship("DataSet", backref="user", lazy=True)
    profile = db.relationship("UserProfile", backref="user", uselist=False)
    recovery_codes = db.relationship(
        "RecoveryCode",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if "password" in kwargs:
            self.set_password(kwargs["password"])

    def __repr__(self):
        return f"<User {self.email}>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def temp_folder(self) -> str:
        from app.features.auth.services import AuthenticationService

        return AuthenticationService().temp_folder_by_user(self)

    # --- 2FA (TOTP) ---------------------------------------------------------

    def generate_totp_secret(self) -> str:
        """Genera un secreto nuevo y lo guarda en el usuario (sin hacer commit)."""
        self.totp_secret = pyotp.random_base32()
        return self.totp_secret

    def get_totp_uri(self, issuer: str = TOTP_ISSUER) -> str:
        """URI otpauth:// que se codifica en el QR para dar de alta la cuenta."""
        if not self.totp_secret:
            raise ValueError("The user has no TOTP secret.")
        return pyotp.TOTP(self.totp_secret).provisioning_uri(name=self.email, issuer_name=issuer)

    def verify_totp(self, code) -> bool:
        """Comprueba un código de 6 dígitos contra el secreto del usuario."""
        if not self.totp_secret or code is None:
            return False
        code = str(code).replace(" ", "").strip()
        if not code.isdigit():
            return False
        return pyotp.TOTP(self.totp_secret).verify(code, valid_window=TOTP_VALID_WINDOW)

    def unused_recovery_codes(self) -> list["RecoveryCode"]:
        return [rc for rc in self.recovery_codes if not rc.is_used]


class RecoveryCode(db.Model):
    """Código de un solo uso para entrar si se pierde el dispositivo TOTP.

    Solo se guarda el hash: el código en claro se enseña una única vez al
    generarlo.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    # SHA-256 en hexadecimal del código normalizado.
    code_hash = db.Column(db.String(64), nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<RecoveryCode {self.id} user={self.user_id} used={self.is_used}>"

    @staticmethod
    def normalize(code) -> str:
        """Ignora mayúsculas, espacios y guiones al comparar."""
        return "".join(ch for ch in str(code).lower() if ch.isalnum())

    @staticmethod
    def hash_code(code) -> str:
        return hashlib.sha256(RecoveryCode.normalize(code).encode()).hexdigest()

    @staticmethod
    def generate_plain_code() -> str:
        """Código aleatorio con formato xxxx-xxxx-xxxx-xxxx."""
        raw = "".join(secrets.choice(RECOVERY_CODE_ALPHABET) for _ in range(RECOVERY_CODE_LENGTH))
        groups = [raw[i : i + RECOVERY_CODE_GROUP] for i in range(0, RECOVERY_CODE_LENGTH, RECOVERY_CODE_GROUP)]
        return "-".join(groups)

    @classmethod
    def from_plain(cls, plain_code: str, **kwargs) -> "RecoveryCode":
        return cls(code_hash=cls.hash_code(plain_code), **kwargs)

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    def matches(self, code) -> bool:
        if code is None:
            return False
        if not self.normalize(code):
            return False
        return hmac.compare_digest(self.code_hash, self.hash_code(code))

    def mark_used(self) -> None:
        self.used_at = datetime.now(timezone.utc)
