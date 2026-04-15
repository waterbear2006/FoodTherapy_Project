"""
[DB] SQLite 数据库封装（供健康档案持久化）
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, DateTime, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "app.db"

# SQLite 在多线程下需允许跨线程连接
engine = create_engine(
    f"sqlite:///{DB_PATH.as_posix()}",
    connect_args={"check_same_thread": False},
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()


class HealthArchive(Base):
    __tablename__ = "health_archive"

    user_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    data_json: Mapped[str] = mapped_column(Text, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


def init_db() -> None:
    """创建表（幂等）"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 初始化表（模块导入即建表）
init_db()

