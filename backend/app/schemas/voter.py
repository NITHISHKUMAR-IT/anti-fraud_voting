import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VoterBase(BaseModel):
    voter_id: str = Field(..., min_length=3, max_length=30)
    full_name: str = Field(..., min_length=2, max_length=120)
    date_of_birth: str = Field(..., description="ISO 8601 date: YYYY-MM-DD")
    constituency: str
    booth_id: str
    gender: str
    phone: Optional[str] = None


class VoterCreate(VoterBase):
    pass


class VoterResponse(VoterBase):
    id: uuid.UUID
    is_active: bool
    has_voted: bool
    voted_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class VoterStatusResponse(BaseModel):
    voter_id: str
    full_name: str
    has_voted: bool
    voted_at: Optional[datetime]
    booth_id: str


class OfficerLoginRequest(BaseModel):
    badge_number: str
    password: str


class OfficerTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    officer_name: str
    booth_id: str
