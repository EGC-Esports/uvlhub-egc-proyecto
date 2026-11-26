"""Unit tests for the auth feature — pure logic, no Flask app, no DB."""

import re
import time

import pyotp
import pytest

from app.features.auth.models import RECOVERY_CODE_ALPHABET, TOTP_ISSUER, RecoveryCode, User

pytestmark = pytest.mark.unit


def test_set_password_hashes_value():
    user = User(email="alice@example.com")
    user.set_password("secret")
    assert user.password != "secret"
    assert user.check_password("secret") is True


def test_check_password_rejects_wrong_value():
    user = User(email="alice@example.com")
    user.set_password("secret")
    assert user.check_password("nope") is False


# --- 2FA: secreto TOTP (WI200-1) ---------------------------------------------


def test_generate_totp_secret_sets_base32_secret():
    user = User(email="alice@example.com")
    secret = user.generate_totp_secret()
    assert user.totp_secret == secret
    assert len(secret) == 32
    assert re.fullmatch(r"[A-Z2-7]+", secret)


def test_generate_totp_secret_changes_every_time():
    user = User(email="alice@example.com")
    assert user.generate_totp_secret() != user.generate_totp_secret()


def test_get_totp_uri_contains_issuer_email_and_secret():
    user = User(email="alice@example.com")
    secret = user.generate_totp_secret()
    uri = user.get_totp_uri()
    assert uri.startswith("otpauth://totp/")
    assert "alice%40example.com" in uri
    assert f"secret={secret}" in uri
    assert f"issuer={TOTP_ISSUER}" in uri


def test_get_totp_uri_without_secret_raises():
    with pytest.raises(ValueError):
        User(email="alice@example.com").get_totp_uri()


def test_verify_totp_accepts_current_code():
    user = User(email="alice@example.com")
    user.generate_totp_secret()
    code = pyotp.TOTP(user.totp_secret).now()
    assert user.verify_totp(code) is True
    assert user.verify_totp(f" {code[:3]} {code[3:]} ") is True


def test_verify_totp_accepts_previous_step_for_clock_drift():
    user = User(email="alice@example.com")
    user.generate_totp_secret()
    previous = pyotp.TOTP(user.totp_secret).at(time.time() - 30)
    assert user.verify_totp(previous) is True


def test_verify_totp_rejects_old_wrong_and_malformed_codes():
    user = User(email="alice@example.com")
    user.generate_totp_secret()
    totp = pyotp.TOTP(user.totp_secret)
    current = totp.now()
    wrong = str((int(current) + 1) % 1_000_000).zfill(6)
    assert user.verify_totp(totp.at(time.time() - 120)) is False
    assert user.verify_totp(wrong) is False
    assert user.verify_totp("abcdef") is False
    assert user.verify_totp("") is False
    assert user.verify_totp(None) is False


def test_verify_totp_without_secret_is_false():
    assert User(email="alice@example.com").verify_totp("123456") is False


# --- 2FA: códigos de recuperación (WI200-1) ----------------------------------


def test_generate_plain_code_format_and_alphabet():
    code = RecoveryCode.generate_plain_code()
    group = rf"[{RECOVERY_CODE_ALPHABET}]{{4}}"
    assert re.fullmatch(rf"{group}-{group}-{group}-{group}", code)


def test_generate_plain_code_is_random():
    codes = {RecoveryCode.generate_plain_code() for _ in range(50)}
    assert len(codes) == 50


def test_recovery_code_stores_only_hash():
    plain = RecoveryCode.generate_plain_code()
    rc = RecoveryCode.from_plain(plain)
    assert plain not in rc.code_hash
    assert RecoveryCode.normalize(plain) not in rc.code_hash


def test_recovery_code_matches_ignoring_case_spaces_and_hyphen():
    plain = RecoveryCode.generate_plain_code()
    rc = RecoveryCode.from_plain(plain)
    assert rc.matches(plain) is True
    assert rc.matches(plain.upper()) is True
    assert rc.matches(plain.replace("-", "")) is True
    assert rc.matches(f"  {plain.replace('-', ' ')} ") is True


def test_recovery_code_rejects_other_codes():
    rc = RecoveryCode.from_plain(RecoveryCode.generate_plain_code())
    assert rc.matches(RecoveryCode.generate_plain_code()) is False
    assert rc.matches("") is False
    assert rc.matches("---") is False
    assert rc.matches(None) is False


def test_recovery_code_mark_used():
    rc = RecoveryCode.from_plain(RecoveryCode.generate_plain_code())
    assert rc.is_used is False
    rc.mark_used()
    assert rc.is_used is True
    assert rc.used_at is not None


def test_unused_recovery_codes_skips_used_ones():
    user = User(email="alice@example.com")
    used = RecoveryCode.from_plain(RecoveryCode.generate_plain_code())
    unused = RecoveryCode.from_plain(RecoveryCode.generate_plain_code())
    used.mark_used()
    user.recovery_codes = [used, unused]
    assert user.unused_recovery_codes() == [unused]
