"""
Indelible Ink Detection Service
---------------------------------
Detects the presence of indelible voting ink on a voter's left index finger
using HSV color-space thresholding in OpenCV.

The ink used in most Indian elections (Camelot M Stencil Ink / similar) is a
violet-blue dye with a characteristic HSV hue in the 100-160° range.

Pipeline:
  1. Decode JPEG/PNG image bytes with OpenCV.
  2. Optionally isolate the central 60% of the image (assumed to be the
     fingertip region - operator should frame the shot accordingly).
  3. Convert BGR → HSV.
  4. Apply an HSV range mask to isolate ink-colored pixels.
  5. Calculate the ratio of ink pixels to total ROI pixels.
  6. Compare against a configurable threshold.

Tuning advice:
  - Adjust INK_HUE_LOW/HIGH in config.py for different ink brands / lighting.
  - Use cv2.inRange preview mode during calibration.
"""

import io
import logging

import cv2
import numpy as np
from PIL import Image

from app.core.config import settings
from app.schemas.verification import InkDetectionResult

logger = logging.getLogger(__name__)


def detect_ink(image_bytes: bytes) -> InkDetectionResult:
    """
    Analyse a fingertip image and return whether indelible ink is present.
    """
    bgr = _bytes_to_bgr(image_bytes)
    if bgr is None:
        return InkDetectionResult(
            ink_present=False,
            ink_ratio=0.0,
            message="Failed to decode image.",
        )

    roi = _extract_fingertip_roi(bgr)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    lower = np.array([settings.INK_HUE_LOW, settings.INK_SAT_LOW, settings.INK_VAL_LOW])
    upper = np.array([settings.INK_HUE_HIGH, settings.INK_SAT_HIGH, settings.INK_VAL_HIGH])
    mask = cv2.inRange(hsv, lower, upper)

    # Small morphological cleanup to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel, iterations=1)

    total_pixels = roi.shape[0] * roi.shape[1]
    ink_pixels = int(np.sum(mask > 0))
    ink_ratio = ink_pixels / total_pixels if total_pixels > 0 else 0.0

    ink_present = ink_ratio >= settings.INK_PIXEL_RATIO_THRESHOLD

    msg = (
        f"Ink detected (ratio={ink_ratio:.4f}, threshold={settings.INK_PIXEL_RATIO_THRESHOLD})"
        if ink_present
        else f"No ink detected (ratio={ink_ratio:.4f}, threshold={settings.INK_PIXEL_RATIO_THRESHOLD})"
    )
    logger.info(msg)

    return InkDetectionResult(
        ink_present=ink_present,
        ink_ratio=round(ink_ratio, 6),
        message=msg,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bytes_to_bgr(image_bytes: bytes):
    """Decode raw image bytes into an OpenCV BGR array."""
    try:
        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return bgr
    except Exception as exc:
        logger.error("Image decode error: %s", exc)
        return None


def _extract_fingertip_roi(bgr: np.ndarray, center_fraction: float = 0.6) -> np.ndarray:
    """
    Crop the central region of the image where the ink mark is expected.
    This reduces false positives from background colours.
    """
    h, w = bgr.shape[:2]
    pad_h = int(h * (1 - center_fraction) / 2)
    pad_w = int(w * (1 - center_fraction) / 2)
    return bgr[pad_h: h - pad_h, pad_w: w - pad_w]
