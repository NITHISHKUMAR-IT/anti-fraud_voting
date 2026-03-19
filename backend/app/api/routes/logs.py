"""Audit log routes - read-only."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_officer
from app.db.session import get_db
from app.models.logs import AuditLog
from app.models.voter import PollingOfficer
from pydantic import BaseModel
from datetime import datetime
import uuid


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    voter_ref: Optional[str]
    booth_id: str
    officer_badge: Optional[str]
    action: str
    result: str
    detail: Optional[str]
    ip_address: Optional[str]
    timestamp: datetime
    model_config = {"from_attributes": True}


router = APIRouter()


@router.get("/", response_model=List[AuditLogResponse])
async def list_logs(
    booth_id: Optional[str] = None,
    voter_ref: Optional[str] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: PollingOfficer = Depends(get_current_officer),
):
    query = select(AuditLog).order_by(desc(AuditLog.timestamp))
    if booth_id:
        query = query.where(AuditLog.booth_id == booth_id)
    if voter_ref:
        query = query.where(AuditLog.voter_ref == voter_ref)
    if action:
        query = query.where(AuditLog.action == action)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
