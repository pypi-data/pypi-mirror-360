from sqlmodel import create_engine, Session
from fp_admin.settings import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


def get_session() -> Session:
    return Session(engine)
