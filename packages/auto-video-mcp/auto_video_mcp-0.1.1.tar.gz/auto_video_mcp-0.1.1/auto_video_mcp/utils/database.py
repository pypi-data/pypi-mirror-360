from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, Optional
import logging
from fastapi import Depends
import os
from dotenv import load_dotenv

from auto_video_mcp.utils.models import Base

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)

# 数据库URL配置，从环境变量获取
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./hifly.db")
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))

# 创建异步数据库引擎
# 使用QueuePool连接池，设置合理的连接池大小
# 对于SQLite，可以考虑使用NullPool避免连接问题
engine = create_async_engine(
    DATABASE_URL,
    echo=DB_ECHO,  # 设置为True可以查看SQL语句
    future=True,
    pool_size=DB_POOL_SIZE,  # 连接池大小
    max_overflow=DB_MAX_OVERFLOW,  # 最大溢出连接数
    pool_timeout=DB_POOL_TIMEOUT,  # 连接超时时间
    pool_recycle=DB_POOL_RECYCLE,  # 连接回收时间，单位秒
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """
    初始化数据库，创建所有表
    """
    try:
        async with engine.begin() as conn:
            logger.info("Creating database tables...")
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖函数，用于FastAPI依赖注入
    """
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


# 创建一个依赖函数，用于FastAPI依赖注入
db_dependency = Callable[[Depends(get_db)], AsyncSession]


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的上下文管理器，可用于with语句
    """
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


async def check_db_connection() -> bool:
    """
    检查数据库连接是否正常
    """
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False 