"""Repository-level tests for auth — UserRepository against the DB."""

import pytest

from app import db
from app.features.auth.models import RecoveryCode
from app.features.auth.repositories import RecoveryCodeRepository, UserRepository

pytestmark = pytest.mark.repository


def test_get_by_email_returns_none_when_absent(test_app):
    with test_app.app_context():
        assert UserRepository().get_by_email("ghost@example.com") is None


def test_create_then_get_by_email(test_app):
    with test_app.app_context():
        repo = UserRepository()
        repo.create(email="dave@example.com", password="davepass")
        found = repo.get_by_email("dave@example.com")
        assert found is not None
        assert found.email == "dave@example.com"
        assert found.check_password("davepass") is True


# --- 2FA: códigos de recuperación (WI200-1) ----------------------------------


def _user_with_codes(email, plain_codes):
    user = UserRepository().create(email=email, password="pass1234")
    user.recovery_codes = [RecoveryCode.from_plain(code) for code in plain_codes]
    db.session.commit()
    return user


def test_two_factor_columns_have_defaults(test_app):
    with test_app.app_context():
        user = UserRepository().create(email="tfa-defaults@example.com", password="pass1234")
        db.session.refresh(user)
        assert user.two_factor_enabled is False
        assert user.totp_secret is None
        assert user.recovery_codes == []


def test_recovery_codes_are_persisted_for_user(test_app):
    with test_app.app_context():
        plain = [RecoveryCode.generate_plain_code() for _ in range(3)]
        user = _user_with_codes("tfa-persist@example.com", plain)
        stored = RecoveryCodeRepository().get_by_user(user.id)
        assert len(stored) == 3
        assert all(rc.user_id == user.id for rc in stored)
        assert [rc.matches(code) for rc, code in zip(stored, plain)] == [True, True, True]


def test_get_unused_by_user_excludes_used_codes(test_app):
    with test_app.app_context():
        plain = [RecoveryCode.generate_plain_code() for _ in range(3)]
        user = _user_with_codes("tfa-unused@example.com", plain)
        repo = RecoveryCodeRepository()
        first = repo.get_by_user(user.id)[0]
        first.mark_used()
        db.session.commit()
        unused = repo.get_unused_by_user(user.id)
        assert len(unused) == 2
        assert first not in unused


def test_get_by_user_only_returns_that_users_codes(test_app):
    with test_app.app_context():
        alice = _user_with_codes("tfa-alice@example.com", [RecoveryCode.generate_plain_code()])
        _user_with_codes("tfa-bob@example.com", [RecoveryCode.generate_plain_code()])
        assert len(RecoveryCodeRepository().get_by_user(alice.id)) == 1


def test_deleting_user_deletes_recovery_codes(test_app):
    with test_app.app_context():
        user = _user_with_codes("tfa-delete@example.com", [RecoveryCode.generate_plain_code()])
        user_id = user.id
        db.session.delete(user)
        db.session.commit()
        assert RecoveryCodeRepository().get_by_user(user_id) == []
