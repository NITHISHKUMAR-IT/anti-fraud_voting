"""Alert management routes."""
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_officer
from app.db.session import get_db
from app.models.alerts import Alert
from app.models.voter import PollingOfficer
from app.schemas.alert import AlertResponse, AlertResolveRequest

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    booth_id: Optional[str] = None,
    unresolved_only: bool = Query(False),
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    officer: PollingOfficer = Depends(get_current_officer),
):
    query = select(Alert).order_by(desc(Alert.created_at))
    if booth_id:
        query = query.where(Alert.booth_id == booth_id)
    if unresolved_only:
        query = query.where(Alert.is_resolved == False)  # noqa: E712
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: str,
    payload: AlertResolveRequest,
    db: AsyncSession = Depends(get_db),
    officer: PollingOfficer = Depends(get_current_officer),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")

    alert.is_resolved = True
    alert.resolved_by = payload.officer_badge
    alert.resolved_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(alert)
    logger.info("Alert %s resolved by %s", alert_id, payload.officer_badge)
    return alert


@router.get("/summary", summary="Alert count summary by severity")
async def alert_summary(
    booth_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: PollingOfficer = Depends(get_current_officer),
):
    from sqlalchemy import func

    query = select(Alert.severity, func.count().label("count"))
    if booth_id:
        query = query.where(Alert.booth_id == booth_id)
    query = query.where(Alert.is_resolved == False).group_by(Alert.severity)  # noqa: E712
    result = await db.execute(query)
    rows = result.fetchall()
    return {row.severity: row.count for row in rows}
