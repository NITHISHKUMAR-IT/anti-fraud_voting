"""
Verification routes
- POST /api/v1/verification/verify  - Full multi-layer verification
- POST /api/v1/verification/enroll  - Enroll biometrics for a voter
"""
import logging
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_officer
from app.db.session import get_db
from app.models.biometric import BiometricData
from app.models.voter import PollingOfficer
from app.models.logs import AuditLog
from app.models.alerts import Alert
from app.schemas.verification import VerificationDecision
from app.services import face_verification, fingerprint_verification, ink_detection
from app.services.decision_engine import make_decision, classify_alert_severity
from app.services.voter_service import get_voter_by_voter_id, mark_voted

router = APIRouter()
logger = logging.getLogger(__name__)


async def _get_biometric(db: AsyncSession, voter_db_id):
    result = await db.execute(
        select(BiometricData).where(BiometricData.voter_id == voter_db_id)
    )
    return result.scalar_one_or_none()


async def _write_audit(db, voter, action, result_str, detail, officer, request_ip=""):
    log = AuditLog(
        voter_id=voter.id if voter else None,
        voter_ref=voter.voter_id if voter else None,
        booth_id=officer.booth_id,
        officer_badge=officer.badge_number,
        action=action,
        result=result_str,
        detail=detail,
        ip_address=request_ip,
    )
    db.add(log)


@router.post("/enroll", summary="Enroll biometrics for a voter")
async def enroll_biometrics(
    voter_id: str = Form(...),
    face_image: UploadFile = File(...),
    fingerprint_scan: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    officer: PollingOfficer = Depends(get_current_officer),
):
    voter = await get_voter_by_voter_id(db, voter_id)
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found.")

    face_bytes = await face_image.read()
    fp_bytes = await fingerprint_scan.read()

    face_enc = face_verification.encode_face(face_bytes)
    if face_enc is None:
        raise HTTPException(status_code=422, detail="No face detected in the uploaded image.")

    fp_template = fingerprint_verification.enroll_fingerprint(fp_bytes)

    existing = await _get_biometric(db, voter.id)
    if existing:
        existing.face_encoding = face_enc
        existing.fingerprint_template = fp_template
    else:
        bio = BiometricData(
            voter_id=voter.id,
            face_encoding=face_enc,
            fingerprint_template=fp_template,
        )
        db.add(bio)

    await _write_audit(db, voter, "VERIFICATION_STARTED", "SUCCESS", "Biometrics enrolled.", officer)
    logger.info("Biometrics enrolled for voter_id=%s by officer=%s", voter_id, officer.badge_number)
    return {"message": "Biometrics enrolled successfully.", "voter_id": voter_id}


@router.post("/verify", response_model=VerificationDecision, summary="Full voter verification")
async def verify_voter(
    voter_id: str = Form(...),
    face_image: UploadFile = File(...),
    fingerprint_scan: UploadFile = File(...),
    finger_image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    officer: PollingOfficer = Depends(get_current_officer),
):
    # 1. Fetch voter record
    voter = await get_voter_by_voter_id(db, voter_id)
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found.")

    biometric = await _get_biometric(db, voter.id)
    if not biometric:
        raise HTTPException(status_code=422, detail="No biometric data enrolled for this voter.")

    # 2. Read uploaded images
    face_bytes = await face_image.read()
    fp_bytes = await fingerprint_scan.read()
    finger_img_bytes = await finger_image.read()

    # 3. Run all checks
    live_face_enc = face_verification.encode_face(face_bytes)
    if live_face_enc is None:
        raise HTTPException(status_code=422, detail="Could not detect a face in the uploaded image.")

    face_result = face_verification.compare_faces(biometric.face_encoding, live_face_enc)
    fp_result = fingerprint_verification.verify_fingerprint(biometric.fingerprint_template, fp_bytes)
    ink_result = ink_detection.detect_ink(finger_img_bytes)

    # 4. Decision engine
    decision = make_decision(
        voter_id=voter_id,
        full_name=voter.full_name,
        has_already_voted=voter.has_voted,
        face_result=face_result,
        fingerprint_result=fp_result,
        ink_result=ink_result,
    )

    # 5. Persist audit log
    audit_action = "VOTE_ALLOWED" if decision.vote_allowed else "VOTE_BLOCKED"
    audit_result = "SUCCESS" if decision.vote_allowed else "FAILURE"
    await _write_audit(db, voter, audit_action, audit_result, decision.reason, officer)

    # 6. Raise alert if needed
    if decision.alert_raised:
        reason_code = decision.reason.split(":")[0]
        alert_type_map = {
            "DUPLICATE_VOTE": "DUPLICATE_VOTE",
            "INK_DETECTED": "INK_DETECTED_ON_ARRIVAL",
            "FACE_MISMATCH": "FACE_MISMATCH",
            "FINGERPRINT_MISMATCH": "FINGERPRINT_MISMATCH",
        }
        alert_type = alert_type_map.get(reason_code, "SYSTEM_ERROR")
        severity = classify_alert_severity(reason_code)

        alert = Alert(
            voter_id=voter.id,
            voter_ref=voter.voter_id,
            booth_id=officer.booth_id,
            severity=severity,
            alert_type=alert_type,
            message=decision.reason,
        )
        db.add(alert)
        await db.flush()
        decision.alert_id = str(alert.id)

    # 7. Mark voter as voted if allowed
    if decision.vote_allowed:
        await mark_voted(db, voter)

    return decision
