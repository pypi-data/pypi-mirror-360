from sqlalchemy import ForeignKey, Text, Integer, DateTime, func, Index, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, MappedColumn, relationship
from datetime import datetime
from .base import Base


class Participant(Base):
    __tablename__ = "participants"
    # ParticipantDto
    # An exception to the Obj_id foreign key naming is participant_id which referes to the relative ID
    # of the participant to other participants in a game.
    participant_id: Mapped[int] = mapped_column(Integer)
    champion_id: Mapped[int] = mapped_column(Integer, ForeignKey("champions.id"))
    puuid: Mapped[str | None] = mapped_column(Text)
    riot_id_game_name: Mapped[str] = mapped_column(Text)
    riot_id_tagline: Mapped[str] = mapped_column(Text)
    summoner_id: Mapped[str | None] = mapped_column(Text)
    summoner_name: Mapped[str | None] = mapped_column(Text)
    team_position: Mapped[str | None] = mapped_column(Text)
    team_id: Mapped[int] = mapped_column(Integer)  # RENAME
    win: Mapped[bool | None] = mapped_column(Boolean)

    # Automatically generate the stored_keys
    PARTICIPANT_DTO = [
        name for name, value in locals().items() if isinstance(value, MappedColumn)
    ]

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(Text, ForeignKey("games.id"))

    game: Mapped["Game"] = relationship("Game", back_populates="participants")
    stats: Mapped["ParticipantStat"] = relationship(
        "ParticipantStat", back_populates="participant"
    )

    team: Mapped["TeamDto"] = relationship(
        "TeamDto",
        primaryjoin="and_(Participant.game_id == TeamDto.game_id, Participant.team_id == TeamDto.team_id)",
        foreign_keys=[game_id, team_id],
        viewonly=True,
    )

    # Debug
    updated: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    @hybrid_property
    def riot_name(self):
        return f"{self.riot_id_game_name}#{self.riot_id_tagline}"

    @riot_name.expression
    def riot_name(cls):
        return func.concat(cls.riot_id_game_name, "#", cls.riot_id_tagline)

    def __repr__(self):
        return f"{self.game_id}-{self.riot_name} (#{self.participant_id})"

    __table_args__ = (
        Index("idx_participants_game_id", "game_id"),
        Index("idx_participants_puuid", "puuid"),
        Index("idx_participants_puuid_queue", "puuid", postgresql_include=["game_id"]),
        Index("idx_participants_champion_id", "champion_id"),
    )
