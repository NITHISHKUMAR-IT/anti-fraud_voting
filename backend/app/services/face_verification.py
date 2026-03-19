"""
Face Verification Service
--------------------------
Primary  : InsightFace (ArcFace backbone, 512-d embeddings) via insightface library.
Fallback : face_recognition (dlib, 128-d embeddings) if InsightFace is not installed.

Both paths produce a cosine-distance score.  A distance below the configured
threshold is considered a match.

Design note: encoding and comparison are kept in separate functions so that
enrollment (store encoding once) and verification (compare at gate) can run
independently without re-loading the model each time.
"""

import logging
import io
import struct
from typing import Optional

import numpy as np
from PIL import Image

from app.core.config import settings
from app.schemas.verification import FaceVerificationResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model loading - lazy-initialised once, shared across all requests
# ---------------------------------------------------------------------------
_face_model = None
_use_insight = False


def _load_model():
    global _face_model, _use_insight
    if _face_model is not None:
        return

    try:
        import insightface
        from insightface.app import FaceAnalysis

        app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        app.prepare(ctx_id=0, det_size=(640, 640))
        _face_model = app
        _use_insight = True
        logger.info("Face model loaded: InsightFace (ArcFace / buffalo_l)")
    except ImportError:
        logger.warning(
            "insightface not installed - falling back to face_recognition (dlib). "
            "Install insightface for higher accuracy."
        )
        import face_recognition  # noqa: F401 - just verifying the import works

        _face_model = "face_recognition"
        _use_insight = False


# ---------------------------------------------------------------------------
# Encoding helpers
# ---------------------------------------------------------------------------

def bytes_to_ndarray(raw: bytes, dtype=np.float32) -> np.ndarray:
    """Deserialise a flat byte blob back into a numpy float32 vector."""
    n = len(raw) // struct.calcsize("f")
    return np.frombuffer(raw, dtype=np.float32).copy()


def ndarray_to_bytes(arr: np.ndarray) -> bytes:
    """Serialise a float32 numpy vector into a flat byte blob."""
    return arr.astype(np.float32).tobytes()


def _pil_to_rgb_array(img_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(img)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def encode_face(image_bytes: bytes) -> Optional[bytes]:
    """
    Extract a face embedding from the supplied image bytes.
    Returns the embedding serialised as bytes, or None if no face is found.
    """
    _load_model()
    rgb = _pil_to_rgb_array(image_bytes)

    if _use_insight:
        faces = _face_model.get(rgb)
        if not faces:
            logger.debug("encode_face: no faces detected by InsightFace")
            return None
        # Pick the largest detected face
        best = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
        return ndarray_to_bytes(best.normed_embedding)

    else:
        import face_recognition

        encs = face_recognition.face_encodings(rgb)
        if not encs:
            logger.debug("encode_face: no faces detected by face_recognition")
            return None
        return ndarray_to_bytes(encs[0])


def compare_faces(
    stored_encoding_bytes: bytes,
    live_encoding_bytes: bytes,
) -> FaceVerificationResult:
    """
    Compare two serialised face embeddings.
    Returns a FaceVerificationResult with matched flag, confidence, and distance.
    """
    stored = bytes_to_ndarray(stored_encoding_bytes)
    live = bytes_to_ndarray(live_encoding_bytes)

    # Cosine distance
    norm_s = np.linalg.norm(stored)
    norm_l = np.linalg.norm(live)

    if norm_s == 0 or norm_l == 0:
        return FaceVerificationResult(
            matched=False,
            confidence=0.0,
            distance=1.0,
            message="Invalid encoding vector (zero norm).",
        )

    cosine_sim = float(np.dot(stored, live) / (norm_s * norm_l))
    # Convert similarity (-1 to 1) to distance (0 to 2); lower = more similar
    distance = 1.0 - cosine_sim
    # Map distance to a 0-1 confidence score (distance 0 → confidence 1)
    confidence = max(0.0, 1.0 - distance)

    matched = distance <= settings.FACE_MATCH_THRESHOLD
    msg = (
        f"Face matched (distance={distance:.4f}, threshold={settings.FACE_MATCH_THRESHOLD})"
        if matched
        else f"Face not matched (distance={distance:.4f}, threshold={settings.FACE_MATCH_THRESHOLD})"
    )

    logger.info(msg)

    return FaceVerificationResult(
        matched=matched,
        confidence=round(confidence, 4),
        distance=round(distance, 4),
        message=msg,
    )
