import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.voter import Voter, PollingOfficer
from app.schemas.voter import VoterCreate

logger = logging.getLogger(__name__)


async def get_voter_by_voter_id(db: AsyncSession, voter_id: str) -> Optional[Voter]:
    result = await db.execute(select(Voter).where(Voter.voter_id == voter_id))
    return result.scalar_one_or_none()


async def create_voter(db: AsyncSession, payload: VoterCreate) -> Voter:
    voter = Voter(**payload.model_dump())
    db.add(voter)
    await db.flush()
    await db.refresh(voter)
    logger.info("Created voter: voter_id=%s", voter.voter_id)
    return voter


async def mark_voted(db: AsyncSession, voter: Voter) -> Voter:
    voter.has_voted = True
    voter.voted_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(voter)
    return voter


async def get_officer_by_badge(db: AsyncSession, badge_number: str) -> Optional[PollingOfficer]:
    result = await db.execute(
        select(PollingOfficer).where(PollingOfficer.badge_number == badge_number)
    )
    return result.scalar_one_or_none()


async def list_voters(db: AsyncSession, booth_id: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = select(Voter)
    if booth_id:
        query = query.where(Voter.booth_id == booth_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_booth_stats(db: AsyncSession, booth_id: str) -> dict:
    from sqlalchemy import func

    total_q = select(func.count()).where(Voter.booth_id == booth_id).select_from(Voter)
    voted_q = select(func.count()).where(Voter.booth_id == booth_id, Voter.has_voted == True).select_from(Voter)

    total = (await db.execute(total_q)).scalar() or 0
    voted = (await db.execute(voted_q)).scalar() or 0

    return {
        "booth_id": booth_id,
        "total_registered": total,
        "total_voted": voted,
        "pending": total - voted,
        "turnout_percent": round((voted / total * 100), 2) if total > 0 else 0.0,
    }
