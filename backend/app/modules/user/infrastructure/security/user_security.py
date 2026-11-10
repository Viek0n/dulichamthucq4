import base64
import hashlib
import hmac
import re
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from cryptography.fernet import Fernet, InvalidToken


class UserSecurity:
    def __init__(
        self,
        encryption_key: str | None,
        lookup_hmac_key: str | None,
        jwt_secret_key: str | None,
        jwt_expiration_minutes: int,
    ):
        if not encryption_key:
            raise RuntimeError("USER_DATA_ENCRYPTION_KEY is required")
        if not lookup_hmac_key or len(lookup_hmac_key.encode("utf-8")) < 32:
            raise RuntimeError("USER_LOOKUP_HMAC_KEY must be at least 32 bytes")
        if not jwt_secret_key or len(jwt_secret_key.encode("utf-8")) < 32:
            raise RuntimeError("JWT_SECRET_KEY must be at least 32 bytes")
        if jwt_expiration_minutes < 1:
            raise RuntimeError("JWT_EXPIRATION_MINUTES must be positive")

        try:
            base64.urlsafe_b64decode(encryption_key.encode("ascii"))
            self._fernet = Fernet(encryption_key.encode("ascii"))
        except (ValueError, UnicodeEncodeError) as error:
            raise RuntimeError(
                "USER_DATA_ENCRYPTION_KEY must be a valid Fernet key"
            ) from error

        self._lookup_hmac_key = lookup_hmac_key.encode("utf-8")
        self._jwt_secret_key = jwt_secret_key
        self.jwt_expiration_minutes = jwt_expiration_minutes

    @staticmethod
    def hash_password(password: str) -> str:
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            raise ValueError("Password must not exceed 72 UTF-8 bytes")
        return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("ascii")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            return False
        try:
            return bcrypt.checkpw(password_bytes, password_hash.encode("ascii"))
        except (ValueError, UnicodeEncodeError):
            return False

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode("utf-8")).decode("ascii")

    def decrypt(self, value: str) -> str:
        try:
            return self._fernet.decrypt(value.encode("ascii")).decode("utf-8")
        except (InvalidToken, UnicodeEncodeError, UnicodeDecodeError) as error:
            raise ValueError("Unable to decrypt user contact data") from error

    def lookup_hash(self, value: str, purpose: str) -> str:
        normalized = value.strip().casefold()
        return hmac.new(
            self._lookup_hmac_key,
            f"{purpose}:{normalized}".encode(),
            hashlib.sha256,
        ).hexdigest()

    def create_access_token(self, user_id: str) -> str:
        now = datetime.now(timezone.utc)
        return jwt.encode(
            {
                "sub": user_id,
                "iat": now,
                "exp": now + timedelta(minutes=self.jwt_expiration_minutes),
            },
            self._jwt_secret_key,
            algorithm="HS256",
        )

    def decode_access_token(self, token: str) -> str:
        try:
            payload = jwt.decode(
                token,
                self._jwt_secret_key,
                algorithms=["HS256"],
                options={"require": ["sub", "exp"]},
            )
        except jwt.InvalidTokenError as error:
            raise ValueError("Invalid or expired access token") from error

        subject = payload.get("sub")
        if not isinstance(subject, str) or not re.fullmatch(
            r"[a-fA-F0-9]{24}", subject
        ):
            raise ValueError("Invalid access token subject")
        return subject
