import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Voter(Base):
    __tablename__ = "voters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    voter_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    date_of_birth: Mapped[str] = mapped_column(String(10), nullable=False)  # ISO 8601
    constituency: Mapped[str] = mapped_column(String(100), nullable=False)
    booth_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    gender: Mapped[str] = mapped_column(
        Enum("MALE", "FEMALE", "OTHER", name="gender_enum"), nullable=False
    )
    phone: Mapped[str] = mapped_column(String(15), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    has_voted: Mapped[bool] = mapped_column(Boolean, default=False)
    voted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    biometric_data = relationship("BiometricData", back_populates="voter", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="voter")
    alerts = relationship("Alert", back_populates="voter")

    def __repr__(self) -> str:
        return f"<Voter voter_id={self.voter_id!r} name={self.full_name!r}>"


class PollingOfficer(Base):
    __tablename__ = "polling_officers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    badge_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    booth_id: Mapped[str] = mapped_column(String(30), nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<PollingOfficer badge={self.badge_number!r}>"
