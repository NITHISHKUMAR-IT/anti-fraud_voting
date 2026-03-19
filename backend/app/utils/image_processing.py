"""Shared image utilities."""
import io
import base64
from typing import Optional
from PIL import Image


def resize_for_model(image_bytes: bytes, max_size: int = 640) -> bytes:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def bytes_to_base64(data: bytes, mime: str = "image/jpeg") -> str:
    encoded = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def validate_image(image_bytes: bytes, max_mb: float = 5.0) -> Optional[str]:
    if len(image_bytes) > max_mb * 1024 * 1024:
        return f"Image exceeds {max_mb} MB limit."
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        return None
    except Exception as e:
        return f"Invalid image: {e}"
