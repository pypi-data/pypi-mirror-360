from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    DateTime,
    Float,
    Index,
    func,
    case,
    type_coerce,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, MappedColumn, relationship
from datetime import datetime
from .base import Base


class ParticipantStat(Base):
    __tablename__ = "participant_stats"
    ### Original MatchV5-named Columns
    kills: Mapped[int] = mapped_column(Integer)
    deaths: Mapped[int] = mapped_column(Integer)
    assists: Mapped[int] = mapped_column(Integer)
    total_minions_killed: Mapped[int] = mapped_column(Integer) # Total *lane* minions killed.
    neutral_minions_killed: Mapped[int] = mapped_column(Integer) # Total *jungle* minions killed.

    # 0 if the item slot is empty. Should be a foreign key in the future.
    item_0: Mapped[int] = mapped_column(Integer, default=0)
    item_1: Mapped[int] = mapped_column(Integer, default=0)
    item_2: Mapped[int] = mapped_column(Integer, default=0)
    item_3: Mapped[int] = mapped_column(Integer, default=0)
    item_4: Mapped[int] = mapped_column(Integer, default=0)
    item_5: Mapped[int] = mapped_column(Integer, default=0)
    item_6: Mapped[int] = mapped_column(Integer, default=0)  # Trinket

    # TODO: Should also be a foreign key
    summoner_1_id: Mapped[int] = mapped_column(Integer)
    summoner_2_id: Mapped[int] = mapped_column(Integer)

    total_damage_dealt: Mapped[int | None] = mapped_column(Integer, nullable=True)
    physical_damage_dealt: Mapped[int | None] = mapped_column(Integer, nullable=True)
    magic_damage_dealt: Mapped[int | None] = mapped_column(Integer, nullable=True)
    true_damage_dealt: Mapped[int | None] = mapped_column(Integer, nullable=True)

    total_damage_dealt_to_champions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    physical_damage_dealt_to_champions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    magic_damage_dealt_to_champions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    true_damage_dealt_to_champions: Mapped[int | None] = mapped_column(Integer, nullable=True)

    total_damage_taken: Mapped[int | None] = mapped_column(Integer, nullable=True)
    physical_damage_taken: Mapped[int | None] = mapped_column(Integer, nullable=True)
    magic_damage_taken: Mapped[int | None] = mapped_column(Integer, nullable=True)
    true_damage_taken: Mapped[int | None] = mapped_column(Integer, nullable=True)

    damage_self_mitigated: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_damage_shielded_on_teammates: Mapped[int | None] = mapped_column(Integer, nullable=True)

    damage_dealt_to_buildings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    damage_dealt_to_turrets: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_damage_dealt_to_champions: Mapped[int | None] = mapped_column(Integer, nullable=True)

    wards_placed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wards_killed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vision_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    total_heals_on_teammates: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_ally_jungle_minions_killed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_enemy_jungle_minions_killed: Mapped[int | None] = mapped_column(Integer, nullable=True)

    champ_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    champ_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)

    basic_pings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    command_pings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    danger_pings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    get_back_pings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    retreat_pings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    on_my_way_pings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    assist_me_pings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    enemy_missing_pings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    push_pings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    all_in_pings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hold_pings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vision_cleared_pings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    enemy_vision_pings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    need_vision_pings: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # The columns defined above can be automatically parsed for MatchV5 inputs
    PARTICIPANT_STAT_DTO = [
        name for name, value in locals().items() if isinstance(value, MappedColumn)
    ]

    ### The following columns require additional processing for MatchV5 inputs
    total_time_CC_dealt: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_CC_ing_others:  Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_gold: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_gold: Mapped[int | None] = mapped_column(Integer, nullable=True)
    perks: Mapped[dict | None] = mapped_column(JSONB)

    ### The following columns must stay nullable
    # stats_update specific column
    position_x: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_y: Mapped[int | None] = mapped_column(Integer, nullable=True) # also refered to as position z
    alive: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    respawn_time: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # This JSONB column to stores the rest of the Match-V5 data for future use
    source_data = mapped_column(JSONB)

    ### Identification Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # game_time is NULL for match_v5 summaries
    game_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    participant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("participants.id")
    )

    participant: Mapped["Participant"] = relationship(
        "Participant", back_populates="stats"
    )

    @classmethod
    def _game_duration_minutes(cls):
        from .participant import Participant
        from .game import Game

        return (
            select(Game.game_duration / 60)
            .join(Participant, Participant.game_id == Game.id)
            .where(Participant.id == cls.participant_id)
            .scalar_subquery()
        )

    @hybrid_property
    def cs(self) -> int:
        return self.total_minions_killed + self.neutral_minions_killed

    @cs.expression
    @classmethod
    def cs(cls):
        return type_coerce(
            cls.total_minions_killed + cls.neutral_minions_killed, Integer
        )

    @hybrid_property
    def cspm(self) -> float | None:
        return self.cs / (self.participant.game.game_duration / 60)

    @cspm.expression
    @classmethod
    def cspm(cls):
        return type_coerce(cls.cs / (cls._game_duration_minutes()), Float)

    @hybrid_property
    def kda(self) -> float:
        if self.deaths > 0:
            return (self.kills + self.assists) / self.deaths
        return self.kills + self.assists

    @kda.expression
    @classmethod
    def kda(cls):
        return case(
            (cls.deaths > 0, (cls.kills + cls.assists) / cls.deaths),
            else_=(cls.kills + cls.assists),
        )

    __table_args__ = (
        Index("idx_participant_stats_participant_time", "participant_id", "game_time"),
        Index("idx_participant_stats_participant_id", "participant_id"),
        Index("idx_participant_stats_game_time", "game_time"),
    )

    # Debug
    updated: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
