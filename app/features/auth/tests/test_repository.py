"""Repository-level tests for auth — UserRepository against the DB."""

import pytest
import sqlalchemy as sa

from app import db
from app.features.auth.models import RecoveryCode, User
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


def _stored_totp_secret(user_id):
    """Valor de la columna tal cual está en la base de datos, sin descifrar."""
    column = User.__table__.c.totp_secret
    query = sa.select(sa.type_coerce(column, sa.String)).where(User.__table__.c.id == user_id)
    return db.session.execute(query).scalar_one()


def test_totp_secret_is_stored_encrypted(test_app):
    with test_app.app_context():
        user = UserRepository().create(email="tfa-encrypted@example.com", password="pass1234")
        secret = user.generate_totp_secret()
        db.session.commit()

        stored = _stored_totp_secret(user.id)
        assert stored is not None
        assert secret not in stored

        db.session.expire(user)
        assert user.totp_secret == secret


def test_unreadable_totp_secret_is_loaded_as_none(test_app):
    with test_app.app_context():
        user = UserRepository().create(email="tfa-unreadable@example.com", password="pass1234")
        # Un valor en claro (o cifrado con otra clave) no se puede descifrar.
        db.session.execute(
            sa.update(User.__table__)
            .where(User.__table__.c.id == user.id)
            .values(totp_secret=sa.type_coerce("JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP", sa.String))
        )
        db.session.commit()

        db.session.expire(user)
        assert user.totp_secret is None
        assert user.verify_totp("123456") is False


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
