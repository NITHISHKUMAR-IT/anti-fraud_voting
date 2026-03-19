"""
Fingerprint Verification Service
----------------------------------
Hardware mode  : Replace the simulate_match() call with calls to your vendor's
                 SDK (e.g. Mantra MFS100 / Secugen / DigitalPersona).
                 The SDK typically exposes a match() function that returns a
                 match score on a 0-100 scale.

Simulation mode: Uses SHA-256 hashing.  The stored template is the hex-digest
                 of the enrolled fingerprint bytes.  During verification the
                 system checks whether the incoming bytes hash to the same value.
                 This is NOT cryptographically sound for real biometrics - it is
                 purely a functional placeholder for development/testing.
"""

import hashlib
import logging

from app.core.config import settings
from app.schemas.verification import FingerprintVerificationResult

logger = logging.getLogger(__name__)

# Set to True once real SDK is wired up
_SDK_AVAILABLE = False


def enroll_fingerprint(raw_scan_bytes: bytes) -> bytes:
    """
    Produce a storable fingerprint template from a raw scan.
    Simulation: returns SHA-256 hex digest encoded as UTF-8 bytes.
    Real SDK : return the ISO 19794-2 template bytes from the SDK.
    """
    if _SDK_AVAILABLE:
        raise NotImplementedError("Wire up your SDK's enroll() call here.")

    digest = hashlib.sha256(raw_scan_bytes).hexdigest()
    logger.debug("Fingerprint enrolled (simulation mode) - digest=%s", digest[:8])
    return digest.encode("utf-8")


def verify_fingerprint(
    stored_template_bytes: bytes,
    live_scan_bytes: bytes,
) -> FingerprintVerificationResult:
    """
    Compare a live scan against a stored template.
    Returns a FingerprintVerificationResult.
    """
    if _SDK_AVAILABLE:
        # SDK path:
        # score = sdk.match(stored_template_bytes, live_scan_bytes)  # int 0-100
        raise NotImplementedError("Wire up your SDK's match() call here.")

    score = _simulate_match(stored_template_bytes, live_scan_bytes)
    matched = score >= settings.FP_MATCH_SCORE_THRESHOLD

    msg = (
        f"Fingerprint matched (score={score}, threshold={settings.FP_MATCH_SCORE_THRESHOLD})"
        if matched
        else f"Fingerprint not matched (score={score}, threshold={settings.FP_MATCH_SCORE_THRESHOLD})"
    )
    logger.info(msg)

    return FingerprintVerificationResult(matched=matched, score=score, message=msg)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _simulate_match(stored: bytes, live: bytes) -> int:
    """
    Simulation-only matcher.
    - Exact hash match  → score 95
    - Otherwise         → score 0

    Replace this with real template matching when hardware is available.
    """
    live_hash = hashlib.sha256(live).hexdigest().encode("utf-8")
    if stored == live_hash:
        return 95
    return 0
