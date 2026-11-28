"""Service-level tests for auth — exercise services + repos with a real DB."""

import pyotp
import pytest

from app import db
from app.features.auth.models import RECOVERY_CODE_COUNT
from app.features.auth.repositories import RecoveryCodeRepository, UserRepository
from app.features.auth.services import AuthenticationService, TwoFactorService

pytestmark = pytest.mark.service


def test_email_available_for_unused_address(test_app):
    with test_app.app_context():
        service = AuthenticationService()
        assert service.is_email_available("ghost@example.com") is True


def test_create_with_profile_persists_user(test_app):
    with test_app.app_context():
        service = AuthenticationService()
        user = service.create_with_profile(
            email="bob@example.com",
            password="bobpass",
            name="Bob",
            surname="Smith",
        )
        assert user.id is not None
        assert service.is_email_available("bob@example.com") is False


# --- 2FA: TwoFactorService (WI200-1) -----------------------------------------


def _new_user(email):
    return UserRepository().create(email=email, password="pass1234")


def _current_code(user):
    return pyotp.TOTP(user.totp_secret).now()


def _wrong_code(user):
    return str((int(_current_code(user)) + 1) % 1_000_000).zfill(6)


def _enabled_user(email):
    user = _new_user(email)
    service = TwoFactorService()
    service.start_setup(user)
    codes = service.enable(user, _current_code(user))
    return user, codes


def test_start_setup_generates_secret_without_enabling(test_app):
    with test_app.app_context():
        user = _new_user("svc-setup@example.com")
        secret = TwoFactorService().start_setup(user)
        db.session.refresh(user)
        assert user.totp_secret == secret
        assert user.two_factor_enabled is False


def test_enable_with_wrong_code_changes_nothing(test_app):
    with test_app.app_context():
        user = _new_user("svc-wrong@example.com")
        service = TwoFactorService()
        service.start_setup(user)
        assert service.enable(user, _wrong_code(user)) is None
        db.session.refresh(user)
        assert user.two_factor_enabled is False
        assert user.recovery_codes == []


def test_enable_without_setup_raises(test_app):
    with test_app.app_context():
        user = _new_user("svc-nosetup@example.com")
        with pytest.raises(ValueError):
            TwoFactorService().enable(user, "123456")


def test_enable_with_valid_code_returns_recovery_codes(test_app):
    with test_app.app_context():
        user, codes = _enabled_user("svc-enable@example.com")
        db.session.refresh(user)
        assert user.two_factor_enabled is True
        assert len(codes) == RECOVERY_CODE_COUNT
        assert len(set(codes)) == RECOVERY_CODE_COUNT
        assert TwoFactorService().remaining_recovery_codes(user) == RECOVERY_CODE_COUNT


def test_setup_and_enable_twice_raise(test_app):
    with test_app.app_context():
        user, _ = _enabled_user("svc-twice@example.com")
        service = TwoFactorService()
        with pytest.raises(ValueError):
            service.start_setup(user)
        with pytest.raises(ValueError):
            service.enable(user, _current_code(user))


def test_verify_totp_requires_two_factor_enabled(test_app):
    with test_app.app_context():
        user = _new_user("svc-verify@example.com")
        service = TwoFactorService()
        service.start_setup(user)
        assert service.verify_totp(user, _current_code(user)) is False
        service.enable(user, _current_code(user))
        assert service.verify_totp(user, _current_code(user)) is True
        assert service.verify_totp(user, _wrong_code(user)) is False


def test_recovery_code_can_only_be_used_once(test_app):
    with test_app.app_context():
        user, codes = _enabled_user("svc-once@example.com")
        service = TwoFactorService()
        assert service.use_recovery_code(user, codes[0].upper()) is True
        assert service.use_recovery_code(user, codes[0]) is False
        assert service.remaining_recovery_codes(user) == RECOVERY_CODE_COUNT - 1


def test_use_recovery_code_rejects_unknown_code(test_app):
    with test_app.app_context():
        user, _ = _enabled_user("svc-unknown@example.com")
        service = TwoFactorService()
        assert service.use_recovery_code(user, "aaaa-aaaa-aaaa-aaaa") is False
        assert service.use_recovery_code(user, "") is False
        assert service.use_recovery_code(user, None) is False
        assert service.remaining_recovery_codes(user) == RECOVERY_CODE_COUNT


def test_regenerate_recovery_codes_invalidates_old_ones(test_app):
    with test_app.app_context():
        user, old_codes = _enabled_user("svc-regen@example.com")
        service = TwoFactorService()
        new_codes = service.regenerate_recovery_codes(user)
        assert len(new_codes) == RECOVERY_CODE_COUNT
        assert service.use_recovery_code(user, old_codes[0]) is False
        assert service.use_recovery_code(user, new_codes[0]) is True
        assert len(RecoveryCodeRepository().get_by_user(user.id)) == RECOVERY_CODE_COUNT


def test_regenerate_without_two_factor_raises(test_app):
    with test_app.app_context():
        with pytest.raises(ValueError):
            TwoFactorService().regenerate_recovery_codes(_new_user("svc-regen-off@example.com"))


def test_disable_clears_secret_and_codes(test_app):
    with test_app.app_context():
        user, codes = _enabled_user("svc-disable@example.com")
        service = TwoFactorService()
        service.disable(user)
        db.session.refresh(user)
        assert user.two_factor_enabled is False
        assert user.totp_secret is None
        assert RecoveryCodeRepository().get_by_user(user.id) == []
        assert service.use_recovery_code(user, codes[0]) is False
