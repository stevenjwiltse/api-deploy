from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

engine = create_engine(str(settings.get_database_url()))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)