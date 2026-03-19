import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: uuid.UUID
    voter_ref: Optional[str]
    booth_id: str
    severity: str
    alert_type: str
    message: str
    is_resolved: bool
    resolved_by: Optional[str]
    resolved_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertResolveRequest(BaseModel):
    officer_badge: str
