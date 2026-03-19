"""Integration & unit tests."""
import io
import numpy as np
import pytest
from app.services.face_verification import ndarray_to_bytes


def test_face_compare_identical():
    from app.services.face_verification import compare_faces
    vec = np.random.rand(128).astype(np.float32)
    vec /= np.linalg.norm(vec)
    enc = ndarray_to_bytes(vec)
    result = compare_faces(enc, enc)
    assert result.matched is True
    assert result.distance < 0.05


def test_face_compare_different():
    from app.services.face_verification import compare_faces
    v1 = np.array([1.0] + [0.0] * 127, dtype=np.float32)
    v2 = np.array([0.0] * 127 + [1.0], dtype=np.float32)
    result = compare_faces(ndarray_to_bytes(v1), ndarray_to_bytes(v2))
    assert result.matched is False


def test_ink_not_detected_white_image():
    from PIL import Image
    from app.services.ink_detection import detect_ink
    buf = io.BytesIO()
    Image.new("RGB", (100, 100), color=(255, 255, 255)).save(buf, format="JPEG")
    result = detect_ink(buf.getvalue())
    assert result.ink_present is False


def test_ink_detected_blue_image():
    from PIL import Image
    from app.services.ink_detection import detect_ink
    buf = io.BytesIO()
    Image.new("RGB", (100, 100), color=(80, 30, 180)).save(buf, format="JPEG")
    result = detect_ink(buf.getvalue())
    assert result.ink_present is True


def _make_face(matched=True):
    from app.schemas.verification import FaceVerificationResult
    return FaceVerificationResult(matched=matched, confidence=0.9, distance=0.1, message="ok")

def _make_fp(matched=True):
    from app.schemas.verification import FingerprintVerificationResult
    return FingerprintVerificationResult(matched=matched, score=80, message="ok")

def _make_ink(present=False):
    from app.schemas.verification import InkDetectionResult
    return InkDetectionResult(ink_present=present, ink_ratio=0.0, message="ok")


def test_decision_allow():
    from app.services.decision_engine import make_decision
    d = make_decision("V001", "Test", False, _make_face(), _make_fp(), _make_ink())
    assert d.vote_allowed is True

def test_decision_block_duplicate():
    from app.services.decision_engine import make_decision
    d = make_decision("V001", "Test", True, _make_face(), _make_fp(), _make_ink())
    assert d.vote_allowed is False
    assert "DUPLICATE" in d.reason

def test_decision_block_ink():
    from app.services.decision_engine import make_decision
    d = make_decision("V001", "Test", False, _make_face(), _make_fp(), _make_ink(present=True))
    assert d.vote_allowed is False

def test_decision_block_face():
    from app.services.decision_engine import make_decision
    d = make_decision("V001", "Test", False, _make_face(matched=False), _make_fp(), _make_ink())
    assert d.vote_allowed is False
