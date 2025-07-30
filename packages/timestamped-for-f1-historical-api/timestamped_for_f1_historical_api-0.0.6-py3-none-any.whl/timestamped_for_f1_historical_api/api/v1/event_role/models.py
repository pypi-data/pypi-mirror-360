from typing import Literal, TYPE_CHECKING

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from timestamped_for_f1_historical_api.core.db import Base, get_base_metadata
from timestamped_for_f1_historical_api.core.models import ResponseModel
# Prevent circular imports for SQLAlchemy models since we are using type annotation
if TYPE_CHECKING:
    from timestamped_for_f1_historical_api.api.v1.event.models import Event
    from timestamped_for_f1_historical_api.api.v1.driver.models import Driver
    


class EventRole(Base):
    __tablename__ = "event_role"
    __table_args__ = (
        PrimaryKeyConstraint("event_id", "driver_id"),
    )
    metadata = get_base_metadata()

    event_id: Mapped[int] = mapped_column(ForeignKey(column="event.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey(column="driver.id"))
    role: Mapped[str] # One of: "initiator" or "participant"

    event: Mapped["Event"] = relationship(back_populates="drivers", cascade="all, delete-orphan")
    driver: Mapped["Driver"] = relationship(back_populates="events", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"EventRole(event_id={self.event_id!r}, driver_id={self.driver_id!r}, role={self.role!r})"


class EventRoleResponse(ResponseModel):
    driver_id: int
    role: Literal["initiator"] | Literal["participant"]