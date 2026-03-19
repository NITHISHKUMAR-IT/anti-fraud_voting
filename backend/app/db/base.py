from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Shared declarative base for all SQLAlchemy models.
    Importing this module causes all model subclasses to be registered,
    which is required before Alembic / init_db can create tables.
    """
    pass


# --- Import all models here so Alembic can discover them ---
from app.models import voter, biometric, logs, alerts  # noqa: F401, E402
