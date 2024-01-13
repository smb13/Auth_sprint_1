from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from core.config import postgres_settings

Base = declarative_base()

engine = create_async_engine(
    postgres_settings.get_dsn(), echo=postgres_settings.echo, future=True
)
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
