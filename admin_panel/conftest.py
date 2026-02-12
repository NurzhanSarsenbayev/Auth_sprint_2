import base64
import time
import uuid

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.contrib.auth import get_user_model
from django.core.cache import cache
from jose import jwt

# ===== RSA utils =====


def _generate_rsa_keypair():
    """Создаём временную RSA пару (приватный/публичный ключ)."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


def _rsa_to_jwk(public_key, kid="test-kid"):
    """Конвертируем публичный ключ в JWK для JWKS."""
    numbers = public_key.public_numbers()
    e = base64.urlsafe_b64encode(
        numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")
    ).rstrip(b"=")
    n = base64.urlsafe_b64encode(
        numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")
    ).rstrip(b"=")

    return {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": kid,
        "n": n.decode(),
        "e": e.decode(),
    }


def _generate_jwt(private_key, kid, payload: dict) -> str:
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return jwt.encode(
        payload,
        pem,
        algorithm="RS256",
        headers={"kid": kid},
    )


# ===== Django users =====


@pytest.fixture
def admin_user(db):
    return get_user_model().objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass",  # Django сам хэширует
    )


@pytest.fixture
def logged_client(client, admin_user):
    """Django test client, залогиненный как суперюзер."""
    assert client.login(username="admin", password="adminpass")
    return client


# ===== RSA keys fixture =====


@pytest.fixture(scope="session")
def rsa_keys():
    """RSA ключи — общие для всей тестовой сессии."""
    priv, pub = _generate_rsa_keypair()
    return {"private": priv, "public": pub, "kid": "test-kid"}


# ===== JWT fixtures =====


@pytest.fixture
def admin_jwt_headers(rsa_keys):
    """JWT с ролью admin."""
    payload = {
        "sub": str(uuid.uuid4()),
        "email": "admin@example.com",
        "role": "admin",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    token = _generate_jwt(rsa_keys["private"], rsa_keys["kid"], payload)

    jwks_key = {"keys": [_rsa_to_jwk(rsa_keys["public"], kid=rsa_keys["kid"])]}
    cache.set("sso:jwks", jwks_key, timeout=600)

    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


@pytest.fixture
def editor_jwt_headers(rsa_keys):
    """JWT с ролью editor."""
    payload = {
        "sub": str(uuid.uuid4()),
        "email": "editor@example.com",
        "role": "editor",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    token = _generate_jwt(rsa_keys["private"], rsa_keys["kid"], payload)

    jwks_key = {"keys": [_rsa_to_jwk(rsa_keys["public"], kid=rsa_keys["kid"])]}
    cache.set("sso:jwks", jwks_key, timeout=600)

    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


@pytest.fixture
def user_jwt_headers(rsa_keys):
    """JWT с ролью user."""
    payload = {
        "sub": str(uuid.uuid4()),
        "email": "user@example.com",
        "role": "user",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    token = _generate_jwt(rsa_keys["private"], rsa_keys["kid"], payload)

    jwks_key = {"keys": [_rsa_to_jwk(rsa_keys["public"], kid=rsa_keys["kid"])]}
    cache.set("sso:jwks", jwks_key, timeout=600)

    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}
