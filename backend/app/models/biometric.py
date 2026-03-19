import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, LargeBinary, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BiometricData(Base):
    """
    Stores encoded biometric templates for each voter.

    face_encoding   : 128-d float32 vector serialised as bytes (face_recognition library)
                      or 512-d vector from InsightFace - stored as raw binary blob.
    fingerprint_template : vendor-specific ISO 19794-2 template bytes.
                           When using simulation mode, stores a SHA-256 hash string.
    """

    __tablename__ = "biometric_data"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    voter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("voters.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    face_encoding: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    face_image_path: Mapped[str | None] = mapped_column(Text, nullable=True)  # reference photo path
    fingerprint_template: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship
    voter = relationship("Voter", back_populates="biometric_data")

    def __repr__(self) -> str:
        return f"<BiometricData voter_id={self.voter_id!r}>"
