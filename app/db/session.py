from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession

from core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
    pool_size=30,
    max_overflow=10
)

sessionlocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)