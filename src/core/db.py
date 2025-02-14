from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession
)
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager


# Temporary individual LocalHost DB until our MySQL DB container is set up
SQL_ALCHEMY_DATABASE_URL = "mysql+aiomysql://root:rootpassword@127.0.0.1:3306/barbershopdb"   


engine = create_async_engine(SQL_ALCHEMY_DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession
)

@asynccontextmanager
async def get_db_session():
    async with AsyncSessionLocal as session:
        yield session