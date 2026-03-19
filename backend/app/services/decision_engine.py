"""
Decision Engine
----------------
Accepts the individual verification results (face, fingerprint, ink detection)
and applies business logic to produce a final allow/block decision.

Rules (in order of precedence):
  1. BLOCK if voter has already voted (duplicate attempt).
  2. BLOCK if ink is detected on arrival (voter has previously voted at another booth).
  3. BLOCK if face does not match stored template.
  4. BLOCK if fingerprint does not match stored template.
  5. ALLOW if all checks pass.

Each BLOCK also triggers an alert with the appropriate severity.
"""

import logging
import uuid

from app.schemas.verification import (
    FaceVerificationResult,
    FingerprintVerificationResult,
    InkDetectionResult,
    VerificationDecision,
)

logger = logging.getLogger(__name__)


def make_decision(
    voter_id: str,
    full_name: str,
    has_already_voted: bool,
    face_result: FaceVerificationResult,
    fingerprint_result: FingerprintVerificationResult,
    ink_result: InkDetectionResult,
) -> VerificationDecision:
    """
    Evaluate all verification results and return a VerificationDecision.
    The caller is responsible for persisting the decision and raising alerts.
    """
    session_id = str(uuid.uuid4())
    alert_raised = False
    alert_id = None

    # --- Rule 1: Duplicate vote attempt ---
    if has_already_voted:
        logger.warning("BLOCK - Duplicate vote attempt: voter_id=%s", voter_id)
        return VerificationDecision(
            voter_id=voter_id,
            full_name=full_name,
            vote_allowed=False,
            reason="DUPLICATE_VOTE: This voter has already cast their vote.",
            face=face_result,
            fingerprint=fingerprint_result,
            ink=ink_result,
            alert_raised=True,  # caller will create alert
            session_id=session_id,
        )

    # --- Rule 2: Ink already present ---
    if ink_result.ink_present:
        logger.warning("BLOCK - Ink detected on arrival: voter_id=%s", voter_id)
        return VerificationDecision(
            voter_id=voter_id,
            full_name=full_name,
            vote_allowed=False,
            reason="INK_DETECTED: Indelible ink is already present on the finger. "
                   "Voter may have voted at another booth.",
            face=face_result,
            fingerprint=fingerprint_result,
            ink=ink_result,
            alert_raised=True,
            session_id=session_id,
        )

    # --- Rule 3: Face mismatch ---
    if not face_result.matched:
        logger.warning("BLOCK - Face mismatch: voter_id=%s distance=%.4f", voter_id, face_result.distance or 0)
        return VerificationDecision(
            voter_id=voter_id,
            full_name=full_name,
            vote_allowed=False,
            reason=f"FACE_MISMATCH: Facial verification failed (confidence={face_result.confidence:.2%}).",
            face=face_result,
            fingerprint=fingerprint_result,
            ink=ink_result,
            alert_raised=True,
            session_id=session_id,
        )

    # --- Rule 4: Fingerprint mismatch ---
    if not fingerprint_result.matched:
        logger.warning("BLOCK - Fingerprint mismatch: voter_id=%s score=%d", voter_id, fingerprint_result.score)
        return VerificationDecision(
            voter_id=voter_id,
            full_name=full_name,
            vote_allowed=False,
            reason=f"FINGERPRINT_MISMATCH: Fingerprint verification failed (score={fingerprint_result.score}).",
            face=face_result,
            fingerprint=fingerprint_result,
            ink=ink_result,
            alert_raised=True,
            session_id=session_id,
        )

    # --- Rule 5: All checks passed → ALLOW ---
    logger.info("ALLOW - All verifications passed: voter_id=%s", voter_id)
    return VerificationDecision(
        voter_id=voter_id,
        full_name=full_name,
        vote_allowed=True,
        reason="All verification checks passed. Voter is authenticated.",
        face=face_result,
        fingerprint=fingerprint_result,
        ink=ink_result,
        alert_raised=False,
        session_id=session_id,
    )


def classify_alert_severity(reason_code: str) -> str:
    """Map a decision reason prefix to an alert severity level."""
    severity_map = {
        "DUPLICATE_VOTE": "CRITICAL",
        "INK_DETECTED": "HIGH",
        "FACE_MISMATCH": "MEDIUM",
        "FINGERPRINT_MISMATCH": "MEDIUM",
    }
    for key, severity in severity_map.items():
        if reason_code.startswith(key):
            return severity
    return "LOW"
