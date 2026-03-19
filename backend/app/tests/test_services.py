"""Unit tests for individual services."""
import pytest
from app.services.fingerprint_verification import enroll_fingerprint, verify_fingerprint


def test_fingerprint_enroll_returns_bytes():
    template = enroll_fingerprint(b"scan_data_12345")
    assert isinstance(template, bytes)
    assert len(template) > 0


def test_fingerprint_exact_match():
    raw = b"voter_fingerprint_abc"
    template = enroll_fingerprint(raw)
    result = verify_fingerprint(template, raw)
    assert result.matched is True
    assert result.score >= 40


def test_fingerprint_no_match():
    template = enroll_fingerprint(b"voter_A")
    result = verify_fingerprint(template, b"voter_B")
    assert result.matched is False
    assert result.score < 40
