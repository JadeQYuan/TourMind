from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # bcrypt 只使用前 72 字节，超过部分会被忽略
    # 为了安全起见，我们在 UTF-8 编码后安全截断到 72 字节
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        # 安全截断到 72 字节，确保不截断多字节字符
        truncated = password_bytes[:72]
        while len(truncated) > 0 and truncated[-1] & 0xC0 == 0x80:
            truncated = truncated[:-1]
        password = truncated.decode("utf-8", errors="ignore")
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    # 对密码进行同样的截断处理
    password_bytes = plain.encode("utf-8")
    if len(password_bytes) > 72:
        truncated = password_bytes[:72]
        while len(truncated) > 0 and truncated[-1] & 0xC0 == 0x80:
            truncated = truncated[:-1]
        plain = truncated.decode("utf-8", errors="ignore")
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: Any, remember_me: bool = False) -> str:
    expire_minutes = (
        settings.REMEMBER_TOKEN_EXPIRE_MINUTES
        if remember_me
        else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
