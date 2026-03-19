import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    voter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("voters.id", ondelete="SET NULL"), nullable=True
    )
    voter_ref: Mapped[str | None] = mapped_column(String(30), nullable=True)
    booth_id: Mapped[str] = mapped_column(String(30), nullable=False)
    severity: Mapped[str] = mapped_column(
        Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="severity_enum"), nullable=False
    )
    alert_type: Mapped[str] = mapped_column(
        Enum(
            "DUPLICATE_VOTE",
            "FACE_MISMATCH",
            "FINGERPRINT_MISMATCH",
            "INK_DETECTED_ON_ARRIVAL",
            "MULTIPLE_FAILED_ATTEMPTS",
            "UNKNOWN_VOTER",
            "SYSTEM_ERROR",
            name="alert_type_enum",
        ),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_by: Mapped[str | None] = mapped_column(String(30), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    voter = relationship("Voter", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert type={self.alert_type!r} severity={self.severity!r}>"
