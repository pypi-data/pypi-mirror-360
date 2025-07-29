from sqlalchemy import BigInteger, Integer, ForeignKey, DateTime, Boolean, Text, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from .base import Base
from ..api.utils import REGIONS


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # This either the actual PUUID as per the Riot API OR Riot Esports API IDs
    puuid: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)  # riotIdgameName
    tagline: Mapped[str] = mapped_column(Text)  # riotIdTagLine
    # Exceptions to the normal Riot API regions include TOURNAMENT (for TR accounts) and RIOT_LOL (for Riot Esports API)
    region: Mapped[str] = mapped_column(Text, nullable=False)
    # Last time / newest game was added to the database (used for match history ingestion)
    latest_game: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    # Player associated with the tracked account
    player_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("players.id"))
    # Flag set for inactive tracked accounts
    skip_update: Mapped[bool] = mapped_column(Boolean, default=False)
    # We use an binary integer flag to save account details.
    account_details: Mapped[int] = mapped_column(Integer, default=0)

    @hybrid_property
    def solo_queue_account(self) -> bool:
        return self.region in REGIONS

    @solo_queue_account.expression
    def solo_queue_account(cls):
        return cls.region.in_(REGIONS)

    player: Mapped["Player"] = relationship("Player", back_populates="accounts")

    def __repr__(self) -> str:
        return f"{self.id} - {self.name}#{self.tagline}, region={self.region}, last_update={self.updated}"

    def __str__(self) -> str:
        return f"{self.name}#{self.tagline}"
