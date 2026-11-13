"""Tests for authentication core logic - no database required."""
import pytest
import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("SYNC_DATABASE_URL", "postgresql://test:test@localhost/test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-123")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/1")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

from app.core.security import hash_password, verify_password, create_access_token, decode_token


def test_password_hash_and_verify():
    plain = "my-secret-password"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)
    assert not verify_password("wrong-password", hashed)


def test_create_and_decode_token():
    payload = {"sub": "user-123", "org_id": "org-456"}
    token = create_access_token(payload)
    assert token
    decoded = decode_token(token)
    assert decoded["sub"] == "user-123"
    assert decoded["org_id"] == "org-456"


def test_token_is_string():
    token = create_access_token({"sub": "u1"})
    assert isinstance(token, str)
    assert len(token) > 20


def test_wrong_password_rejected():
    hashed = hash_password("correct")
    assert not verify_password("incorrect", hashed)


def test_different_hashes_for_same_password():
    pw = "same-password"
    h1 = hash_password(pw)
    h2 = hash_password(pw)
    # bcrypt uses salts, so hashes differ
    assert h1 != h2
    assert verify_password(pw, h1)
    assert verify_password(pw, h2)
