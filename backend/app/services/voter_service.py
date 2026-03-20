import logging
import uuid
import random
from datetime import datetime, timezone, timedelta
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


async def get_officer_by_phone(db: AsyncSession, phone_number: str) -> Optional[PollingOfficer]:
    result = await db.execute(
        select(PollingOfficer).where(PollingOfficer.phone == phone_number)
    )
    return result.scalar_one_or_none()


def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))


async def generate_and_store_otp(db: AsyncSession, officer: PollingOfficer, otp_expiry_minutes: int = 5) -> str:
    """Generate OTP and store it in the database"""
    otp = generate_otp()
    officer.otp = otp
    officer.otp_expires = datetime.now(timezone.utc) + timedelta(minutes=otp_expiry_minutes)
    await db.flush()
    logger.info(f"OTP generated for officer: {officer.badge_number}")
    # In production, send OTP via SMS to officer.phone
    return otp


async def verify_otp(db: AsyncSession, officer: PollingOfficer, otp: str) -> bool:
    """Verify OTP and return True if valid"""
    if not officer.otp or not officer.otp_expires:
        return False
    
    if datetime.now(timezone.utc) > officer.otp_expires:
        logger.warning(f"OTP expired for officer: {officer.badge_number}")
        return False
    
    if officer.otp != otp:
        logger.warning(f"Invalid OTP attempt for officer: {officer.badge_number}")
        return False
    
    # Clear OTP after successful verification
    officer.otp = None
    officer.otp_expires = None
    await db.flush()
    logger.info(f"OTP verified for officer: {officer.badge_number}")
    return True
