from sqlalchemy import Integer, Text, ForeignKey, Boolean, DateTime, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .base import Base


class TeamDto(Base):
    __tablename__ = "team_dtos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(Text, ForeignKey("games.id"))

    # TeamDto
    bans = mapped_column(JSONB)
    objectives = mapped_column(JSONB)
    team_id: Mapped[int] = mapped_column(Integer)
    win: Mapped[bool] = mapped_column(Boolean)

    fk_team_id: Mapped[str | None] = mapped_column(
        Text, ForeignKey("teams.id"), nullable=True
    )

    # Debug
    updated: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    participants: Mapped[list["Participant"]] = relationship(
        "Participant",
        primaryjoin="and_(TeamDto.game_id == Participant.game_id, TeamDto.team_id == Participant.team_id)",
        foreign_keys="[Participant.game_id, Participant.team_id]",
        viewonly=True,
    )

    __table_args__ = (
        Index("idx_team_dtos_game_id", "game_id"),
        Index("idx_team_dtos_fk_team_id", "fk_team_id"),
    )
