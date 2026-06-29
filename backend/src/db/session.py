from collections.abc import Iterator

from app.settings import AppSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def create_session_factory(settings: AppSettings | None = None) -> sessionmaker[Session]:
    """Create the SQLAlchemy session factory used by API dependencies."""
    resolved_settings = settings or AppSettings()
    engine = create_engine(resolved_settings.database_url)
    return sessionmaker(bind=engine, expire_on_commit=False)


SessionFactory = create_session_factory()


def get_db_session() -> Iterator[Session]:
    """Yield one database session for a FastAPI request."""
    with SessionFactory() as session:
        yield session
