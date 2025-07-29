from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models import Base


def get_session_factory(database_url: str, read_only: bool = False):
    engine = create_engine(database_url, pool_recycle=3600)
    if not read_only:
        Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=True, bind=engine)
