from typing import Optional
from pydantic import BaseModel, Field


class FaceVerificationResult(BaseModel):
    matched: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    distance: Optional[float] = None
    message: str


class FingerprintVerificationResult(BaseModel):
    matched: bool
    score: int = Field(..., ge=0, le=100)
    message: str


class InkDetectionResult(BaseModel):
    ink_present: bool
    ink_ratio: float = Field(..., ge=0.0)
    message: str


class VerificationRequest(BaseModel):
    voter_id: str
    booth_id: str
    officer_badge: str


class VerificationDecision(BaseModel):
    voter_id: str
    full_name: Optional[str] = None
    vote_allowed: bool
    reason: str
    face: Optional[FaceVerificationResult] = None
    fingerprint: Optional[FingerprintVerificationResult] = None
    ink: Optional[InkDetectionResult] = None
    alert_raised: bool = False
    alert_id: Optional[str] = None
    session_id: str
