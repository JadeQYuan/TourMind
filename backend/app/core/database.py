
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# 仅在非 Alembic 迁移时创建 async engine
import os
if not os.environ.get("ALEMBIC_RUN", "").lower() == "true":
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from app.core.config import settings
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
