import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AuditLog(Base):
    """
    Immutable record of every verification attempt.
    Rows are never updated or deleted - only inserted.
    """

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    voter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("voters.id", ondelete="SET NULL"), nullable=True
    )
    voter_ref: Mapped[str | None] = mapped_column(String(30), nullable=True)  # human-readable voter_id
    booth_id: Mapped[str] = mapped_column(String(30), nullable=False)
    officer_badge: Mapped[str | None] = mapped_column(String(30), nullable=True)
    action: Mapped[str] = mapped_column(
        Enum(
            "VERIFICATION_STARTED",
            "FACE_MATCHED",
            "FACE_FAILED",
            "FINGERPRINT_MATCHED",
            "FINGERPRINT_FAILED",
            "INK_DETECTED",
            "INK_NOT_DETECTED",
            "VOTE_ALLOWED",
            "VOTE_BLOCKED",
            "DUPLICATE_ATTEMPT",
            "OFFICER_LOGIN",
            "OFFICER_LOGOUT",
            name="audit_action_enum",
        ),
        nullable=False,
    )
    result: Mapped[str] = mapped_column(
        Enum("SUCCESS", "FAILURE", "WARNING", name="audit_result_enum"), nullable=False
    )
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    voter = relationship("Voter", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog action={self.action!r} result={self.result!r} ts={self.timestamp}>"
