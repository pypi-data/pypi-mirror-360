from sqlalchemy import ForeignKey, Text, Integer, DateTime, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from .base import Base
from ..utils.constants import SeriesStatus, SeriesType


class Series(Base):
    __tablename__ = "series"
    ###          1:1 GRID          ###
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    type: Mapped[SeriesType]  # GRID SeriesType
    scheduled_start_time: Mapped[datetime] = mapped_column(DateTime)
    format: Mapped[int] = mapped_column(Integer)  # Best of number
    tournament_id: Mapped[str] = mapped_column(Text, ForeignKey("tournaments.id"))
    external_links = mapped_column(JSONB)

    ###     Processing status      ###
    status: Mapped[SeriesStatus]

    ###           Debug            ###
    updated: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_series_tournament_id", "tournament_id"),
    )
