import os

from flask_login import current_user, login_user
from splent_framework.configuration.configuration import uploads_folder_name
from splent_framework.services.BaseService import BaseService

from app.features.auth.models import RECOVERY_CODE_COUNT, RecoveryCode, User
from app.features.auth.repositories import RecoveryCodeRepository, UserRepository
from app.features.profile.models import UserProfile
from app.features.profile.repositories import UserProfileRepository


class AuthenticationService(BaseService):
    def __init__(self):
        super().__init__(UserRepository())
        self.user_profile_repository = UserProfileRepository()

    def login(self, email, password, remember=True):
        user = self.repository.get_by_email(email)
        if user is not None and user.check_password(password):
            login_user(user, remember=remember)
            return True
        return False

    def is_email_available(self, email: str) -> bool:
        return self.repository.get_by_email(email) is None

    def create_with_profile(self, **kwargs):
        try:
            email = kwargs.pop("email", None)
            password = kwargs.pop("password", None)
            name = kwargs.pop("name", None)
            surname = kwargs.pop("surname", None)

            if not email:
                raise ValueError("Email is required.")
            if not password:
                raise ValueError("Password is required.")
            if not name:
                raise ValueError("Name is required.")
            if not surname:
                raise ValueError("Surname is required.")

            user_data = {"email": email, "password": password}

            profile_data = {
                "name": name,
                "surname": surname,
            }

            user = self.create(commit=False, **user_data)
            profile_data["user_id"] = user.id
            self.user_profile_repository.create(**profile_data)
            self.repository.session.commit()
        except Exception as exc:
            self.repository.session.rollback()
            raise exc
        return user

    def get_authenticated_user(self) -> User | None:
        if current_user.is_authenticated:
            return current_user
        return None

    def get_authenticated_user_profile(self) -> UserProfile | None:
        if current_user.is_authenticated:
            return current_user.profile
        return None

    def temp_folder_by_user(self, user: User) -> str:
        return os.path.join(uploads_folder_name(), "temp", str(user.id))


class TwoFactorService(BaseService):
    """Operaciones sobre el secreto TOTP y los códigos de recuperación.

    Flujo previsto: start_setup() genera el secreto (2FA aún desactivado) para
    pintar el QR; enable() lo activa al confirmar un primer código y devuelve
    los códigos de recuperación en claro, que solo se enseñan esa vez.
    """

    def __init__(self):
        super().__init__(RecoveryCodeRepository())

    def _commit(self):
        try:
            self.repository.session.commit()
        except Exception:
            self.repository.session.rollback()
            raise

    def start_setup(self, user: User) -> str:
        """Genera un secreto nuevo sin activar el 2FA. Devuelve el secreto."""
        if user.two_factor_enabled:
            raise ValueError("Two-factor authentication is already enabled.")
        secret = user.generate_totp_secret()
        self._commit()
        return secret

    def enable(self, user: User, code: str) -> list[str] | None:
        """Activa el 2FA si el código es válido.

        Devuelve los códigos de recuperación en claro, o None si el código no
        es válido (y entonces no cambia nada).
        """
        if user.two_factor_enabled:
            raise ValueError("Two-factor authentication is already enabled.")
        if not user.totp_secret:
            raise ValueError("Call start_setup before enabling two-factor authentication.")
        if not user.verify_totp(code):
            return None
        user.two_factor_enabled = True
        plain_codes = self._replace_recovery_codes(user)
        self._commit()
        return plain_codes

    def disable(self, user: User) -> None:
        """Desactiva el 2FA y borra el secreto y los códigos de recuperación."""
        user.two_factor_enabled = False
        user.totp_secret = None
        user.recovery_codes = []
        self._commit()

    def regenerate_recovery_codes(self, user: User) -> list[str]:
        """Invalida los códigos anteriores y devuelve los nuevos en claro."""
        if not user.two_factor_enabled:
            raise ValueError("Two-factor authentication is not enabled.")
        plain_codes = self._replace_recovery_codes(user)
        self._commit()
        return plain_codes

    def verify_totp(self, user: User, code: str) -> bool:
        return bool(user.two_factor_enabled) and user.verify_totp(code)

    def use_recovery_code(self, user: User, code: str) -> bool:
        """Consume un código de recuperación. True si era válido y no estaba usado."""
        if not user.two_factor_enabled or code is None or not RecoveryCode.normalize(code):
            return False
        recovery_code = self.repository.get_unused_by_user_and_hash(user.id, RecoveryCode.hash_code(code))
        if recovery_code is None:
            return False
        recovery_code.mark_used()
        self._commit()
        return True

    def remaining_recovery_codes(self, user: User) -> int:
        return len(self.repository.get_unused_by_user(user.id))

    def _replace_recovery_codes(self, user: User, count: int = RECOVERY_CODE_COUNT) -> list[str]:
        # delete-orphan en User.recovery_codes borra los anteriores al hacer commit.
        plain_codes = [RecoveryCode.generate_plain_code() for _ in range(count)]
        user.recovery_codes = [RecoveryCode.from_plain(code) for code in plain_codes]
        return plain_codes
