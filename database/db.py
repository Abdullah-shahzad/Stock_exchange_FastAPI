from sqlalchemy import create_engine, NullPool
from sqlalchemy.ext.declarative import declarative_base
from config.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

db_url = settings.DATABASE_URL



engine = create_async_engine(db_url, echo=True)

async_session = (sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
))

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
