from sqlalchemy import (
    ForeignKey,
    Text,
    Integer,
    BigInteger,
    DateTime,
    func,
    Index,
    text,
    Boolean,
    case,
    literal
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, MappedColumn
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.sqltypes import DateTime
from datetime import datetime
from .base import Base
from ..api.utils import REGIONS


class Game(Base):
    __tablename__ = "games"
    # InfoDto
    end_of_game_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    game_duration: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # in seconds
    game_id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True
    )  # Riot's game id
    game_mode: Mapped[str | None] = mapped_column(Text, nullable=True)
    game_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    game_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    game_version: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Riot game version
    map_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    platform_id: Mapped[str | None] = mapped_column(Text, nullable=True)  # e.g. EUW1
    queue_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tournament_code: Mapped[str | None] = mapped_column(Text, nullable=True)

    INFO_DTO = [
        name for name, value in locals().items() if isinstance(value, MappedColumn)
    ]

    game_creation: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    game_start_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    game_end_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    TIMESTAMPS = [
        name for name, value in locals().items() if isinstance(value, MappedColumn) and isinstance(value.column.type, DateTime)
    ]

    # Equivalent to matchId in the MatchV5 API (e.x. NA1_12345)
    id: Mapped[str] = mapped_column(Text, primary_key=True)

    game_ended_in_early_surrender: Mapped[bool | None] = mapped_column(Boolean)
    game_ended_in_surrender: Mapped[bool | None] = mapped_column(Boolean)

    # Additional game information can be stored here.
    source_data = mapped_column(JSONB)

    # Esports Game Information
    series_id: Mapped[str | None] = mapped_column(Text, ForeignKey("series.id"), nullable=True)
    series_game_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Debug
    updated: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # ParticipantDto
    participants: Mapped[list["Participant"]] = relationship(
        "Participant", back_populates="game"
    )
    # TeamDto
    teams: Mapped[list["TeamDto"]] = relationship()

    @hybrid_property
    def patch(self):  # type: ignore
        version_split = self.game_version.split(".")
        return (
            f"{version_split[0]}.{version_split[1]}"
            if len(version_split) >= 2
            else None
        )

    @patch.expression
    def patch(cls):
        return func.concat(
            func.split_part(cls.game_version, ".", 1),
            ".",
            func.split_part(cls.game_version, ".", 2),
        )

    @hybrid_property
    def solo_queue(self) -> bool: # type: ignore
        return self.platform_id in list(REGIONS)

    @solo_queue.expression
    def solo_queue(cls):
        return cls.platform_id.in_(list(REGIONS))

    @hybrid_property
    def calculated_game_type(self) -> str: # type: ignore
        if self.solo_queue and self.queue_id == 420:
            return "SOLOQUEUE"
        elif self.solo_queue and self.queue_id == 0: # Tournament code games
            return "CUSTOM"
        elif not self.solo_queue and self.game_name and self.game_name.lower().startswith("scrim|"):
            return "SCRIM"
        elif not self.solo_queue:
            return "ESPORTS"
        else:
            return ""

    @calculated_game_type.expression
    @classmethod
    def calculated_game_type(cls):
        return case(
            (cls.solo_queue.is_(True) & (cls.queue_id == 420), literal("SOLOQUEUE")),
            (cls.solo_queue.is_(True) & (cls.queue_id == 0), literal("CUSTOM")),
            (cls.solo_queue.is_(False) & cls.game_name.ilike("scrim|%"), literal("SCRIM")),
            (cls.solo_queue.is_(False), literal("ESPORTS")),
            else_=literal("")
        )

    __table_args__ = (
        Index("idx_games_queue_id", "queue_id"),
        Index("idx_games_end_timestamp", text("game_end_timestamp DESC")),
        Index("idx_game_queue_timestamp", "queue_id", text("game_end_timestamp DESC")),
        Index("idx_games_game_type", "game_type"),
        Index("idx_games_series_id", "series_id"),
        Index("idx_games_game_version", "game_version"),
        Index("idx_games_type_version", "game_type", "game_version"),
    )
