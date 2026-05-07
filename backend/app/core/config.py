from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json


import os

class Settings(BaseSettings):
    # 支持通用配置在.env，环境配置在.env.{env}，后者覆盖前者
    ENV: str = os.getenv("ENV", "dev")
    model_config = SettingsConfigDict(
        env_file=[".env", f".env.{os.getenv('ENV', 'dev')}"] ,
        env_file_encoding="utf-8"
    )

    # 数据库
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    REMEMBER_TOKEN_EXPIRE_MINUTES: int = 10080

    # 文件上传
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # 其他
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


settings = Settings()
