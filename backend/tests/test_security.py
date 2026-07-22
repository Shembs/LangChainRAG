"""Tests for app.core.security — password hashing & JWT tokens."""
import pytest
from datetime import timedelta
from unittest.mock import patch

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


# ──────────────────────────────────────────────
# Password Hashing
# ──────────────────────────────────────────────

class TestHashPassword:
    """hash_password() — bcrypt 密码哈希"""

    def test_returns_string(self):
        result = hash_password("mypassword")
        assert isinstance(result, str)

    def test_returns_bcrypt_prefix(self):
        result = hash_password("secret123")
        assert result.startswith("$2b$") or result.startswith("$2a$")

    def test_salt_produces_different_hashes(self):
        """相同密码两次哈希产生不同结果（bcrypt 随机盐）"""
        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2

    def test_empty_password(self):
        result = hash_password("")
        assert isinstance(result, str)

    def test_unicode_chinese_password(self):
        result = hash_password("密码123!@#测试")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_very_long_password(self):
        """长密码（但不超过 bcrypt 72 字节限制）"""
        long_pw = "a" * 70
        result = hash_password(long_pw)
        assert isinstance(result, str)


class TestVerifyPassword:
    """verify_password() — bcrypt 密码验证"""

    def test_correct_password_returns_true(self):
        hashed = hash_password("correct_horse_battery")
        assert verify_password("correct_horse_battery", hashed) is True

    def test_wrong_password_returns_false(self):
        hashed = hash_password("correct_horse_battery")
        assert verify_password("wrong_password", hashed) is False

    def test_case_sensitive(self):
        hashed = hash_password("CaseSensitive")
        assert verify_password("casesensitive", hashed) is False
        assert verify_password("CaseSensitive", hashed) is True

    def test_empty_vs_nonempty(self):
        hashed = hash_password("")
        assert verify_password("something", hashed) is False
        assert verify_password("", hashed) is True

    def test_similar_but_different(self):
        hashed = hash_password("password123")
        assert verify_password("password124", hashed) is False


# ──────────────────────────────────────────────
# JWT Tokens
# ──────────────────────────────────────────────

TEST_SECRET = "test-secret-key-for-unit-tests"
TEST_ALGORITHM = "HS256"

@pytest.fixture(autouse=True)
def mock_settings():
    """所有 JWT 测试统一 Mock settings，避免依赖真实 .env"""
    with (
        patch("app.core.security.settings.jwt_secret_key", TEST_SECRET),
        patch("app.core.security.settings.jwt_algorithm", TEST_ALGORITHM),
        patch("app.core.security.settings.access_token_expire_minutes", 30),
        patch("app.core.security.settings.refresh_token_expire_days", 7),
    ):
        yield


class TestCreateAccessToken:
    """create_access_token() — 生成 Access Token"""

    def test_returns_string(self):
        token = create_access_token(subject="user-1")
        assert isinstance(token, str)
        assert len(token) > 20

    def test_token_is_decodable(self):
        token = create_access_token(subject="user-1")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-1"

    def test_subject_converted_to_string(self):
        token = create_access_token(subject=42)
        payload = decode_token(token)
        assert payload["sub"] == "42"

    def test_default_expiry_set(self):
        """不传 expires_delta → 使用 settings 默认值"""
        with patch("app.core.security.settings.access_token_expire_minutes", 30):
            token = create_access_token(subject="user-1")
        payload = decode_token(token)
        assert "exp" in payload

    def test_custom_expiry(self):
        token = create_access_token(subject="user-1", expires_delta=timedelta(minutes=5))
        payload = decode_token(token)
        assert "exp" in payload

    def test_different_subjects_produce_different_tokens(self):
        t1 = create_access_token(subject="user-a")
        t2 = create_access_token(subject="user-b")
        assert t1 != t2


class TestCreateRefreshToken:
    """create_refresh_token() — 生成 Refresh Token"""

    def test_returns_string(self):
        token = create_refresh_token(subject="user-1")
        assert isinstance(token, str)

    def test_token_is_decodable(self):
        token = create_refresh_token(subject="user-1")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-1"

    def test_has_refresh_type_field(self):
        token = create_refresh_token(subject="user-1")
        payload = decode_token(token)
        assert payload["type"] == "refresh"

    def test_subject_converted_to_string(self):
        token = create_refresh_token(subject=99)
        payload = decode_token(token)
        assert payload["sub"] == "99"


class TestDecodeToken:
    """decode_token() — 解码 JWT Token"""

    def test_valid_token_returns_payload(self):
        token = create_access_token(subject="user-1")
        payload = decode_token(token)
        assert isinstance(payload, dict)
        assert "sub" in payload
        assert "exp" in payload

    def test_expired_token_returns_none(self):
        """过期 token → 返回 None"""
        with patch("app.core.security.settings.access_token_expire_minutes", -1):
            token = create_access_token(subject="user-1")
        payload = decode_token(token)
        assert payload is None

    def test_garbage_token_returns_none(self):
        assert decode_token("not.a.valid.jwt.token!!!") is None

    def test_empty_string_returns_none(self):
        assert decode_token("") is None

    def test_none_input_raises_attribute_error(self):
        """None 输入会直接崩（源码未防御 None），建议源码增加 None 检查"""
        # 当前实现：jose 内部对 None 做 .rsplit(b".") → AttributeError
        # 改进建议：在 decode_token 开头加 `if token is None: return None`
        with pytest.raises(AttributeError):
            decode_token(None)

    def test_tampered_token_returns_none(self):
        """篡改 payload 的 token → 签名验证失败"""
        token = create_access_token(subject="user-1")
        # 改变最后一个字符，破坏签名
        tampered = token[:-1] + ("Z" if token[-1] != "Z" else "X")
        result = decode_token(tampered)
        assert result is None

    def test_wrong_secret_returns_none(self):
        """用错误密钥生成的 token → 解码失败"""
        with patch("app.core.security.settings.jwt_secret_key", "wrong-secret"):
            token = create_access_token(subject="user-1")
        payload = decode_token(token)
        assert payload is None
