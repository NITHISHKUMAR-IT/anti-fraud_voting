"""
Voter routes
- POST /api/v1/voters/         - Register a voter
- GET  /api/v1/voters/{id}     - Get voter info
- GET  /api/v1/voters/         - List voters (officer only)
- POST /api/v1/voters/login    - Officer login → JWT
- GET  /api/v1/voters/stats/{booth_id} - Booth-level turnout
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_officer
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.voter import PollingOfficer
from app.schemas.voter import (
    OfficerLoginRequest,
    OfficerTokenResponse,
    VoterCreate,
    VoterResponse,
    VoterStatusResponse,
)
from app.services import voter_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=OfficerTokenResponse, summary="Officer login")
async def officer_login(payload: OfficerLoginRequest, db: AsyncSession = Depends(get_db)):
    officer = await voter_service.get_officer_by_badge(db, payload.badge_number)
    if not officer or not verify_password(payload.password, officer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid badge number or password.",
        )
    if not officer.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive.")

    officer.last_login = datetime.now(timezone.utc)
    await db.flush()

    token = create_access_token(subject=officer.badge_number)
    logger.info("Officer logged in: badge=%s", officer.badge_number)
    return OfficerTokenResponse(
        access_token=token,
        officer_name=officer.name,
        booth_id=officer.booth_id,
    )


@router.post("/", response_model=VoterResponse, status_code=status.HTTP_201_CREATED)
async def register_voter(
    payload: VoterCreate,
    db: AsyncSession = Depends(get_db),
    _: PollingOfficer = Depends(get_current_officer),
):
    existing = await voter_service.get_voter_by_voter_id(db, payload.voter_id)
    if existing:
        raise HTTPException(status_code=409, detail="Voter ID already registered.")
    voter = await voter_service.create_voter(db, payload)
    return voter


@router.get("/stats/{booth_id}", summary="Turnout stats for a booth")
async def booth_stats(
    booth_id: str,
    db: AsyncSession = Depends(get_db),
    _: PollingOfficer = Depends(get_current_officer),
):
    return await voter_service.get_booth_stats(db, booth_id)


@router.get("/{voter_id}", response_model=VoterStatusResponse)
async def get_voter_status(
    voter_id: str,
    db: AsyncSession = Depends(get_db),
    _: PollingOfficer = Depends(get_current_officer),
):
    voter = await voter_service.get_voter_by_voter_id(db, voter_id)
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found.")
    return voter


@router.get("/", response_model=List[VoterResponse])
async def list_voters(
    booth_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: PollingOfficer = Depends(get_current_officer),
):
    return await voter_service.list_voters(db, booth_id=booth_id, skip=skip, limit=limit)
