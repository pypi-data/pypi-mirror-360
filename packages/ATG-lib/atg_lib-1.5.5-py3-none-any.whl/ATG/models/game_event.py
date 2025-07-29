from sqlalchemy import Integer, Text, ForeignKey, DateTime, func, Index
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class GameEvent(Base):
    __tablename__ = "game_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(Text, ForeignKey("games.id"))
    # rfc461Schema (identifies the event type)
    schema: Mapped[str] = mapped_column(Text)
    sequence_index: Mapped[int] = mapped_column(Integer)
    # Missing from 'champ_select', 'game_info' type events
    game_time: Mapped[int] = mapped_column(Integer)

    # The rest of the event data is stored here
    source_data = mapped_column(JSONB)

    # Debug
    updated: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_game_events_game_id", "game_id"),
        Index("idx_game_events_game_id_game_time", "game_id", "game_time"),
        Index("idx_game_events_game_id_schema", "game_id", "schema"),
        Index(
            "idx_game_events_game_id_schema_seq", "game_id", "schema", "sequence_index"
        ),
        Index("idx_game_events_game_id_schema_time", "game_id", "schema", "game_time"),
        Index("idx_game_events_schema", "schema"),
    )
