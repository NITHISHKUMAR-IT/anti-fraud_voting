import logging

from sqlalchemy import text

from app.db.session import engine
from app.db.base import Base
from app.core.security import hash_password

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """
    Creates all tables (if they don't exist) and seeds an initial admin officer
    so the system is usable right after first boot.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await _seed_default_officer()
    logger.info("Database tables ready.")


async def _seed_default_officer() -> None:
    """Insert a default polling officer only when the officers table is empty."""
    from app.db.session import AsyncSessionLocal
    from app.models.voter import PollingOfficer

    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM polling_officers"))
        count = result.scalar()
        if count == 0:
            default_officer = PollingOfficer(
                name="Admin Officer",
                badge_number="ADMIN-001",
                booth_id="BOOTH-DEFAULT",
                hashed_password=hash_password("Admin@123"),
                is_active=True,
            )
            session.add(default_officer)
            await session.commit()
            logger.info(
                "Seeded default officer: badge=ADMIN-001, password=Admin@123 "
                "(CHANGE THIS IMMEDIATELY in production)"
            )
