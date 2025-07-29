from sqlalchemy import Integer, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base
from .account import Account
from datetime import datetime


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Not sure how to deal with naming conflicts. For now, we assume that names can be repeated but we can use the column below.
    name: Mapped[str] = mapped_column(Text)
    # We store the name used on Leaguepedia/Oracles Elixer here for easier use with those services.
    # For now, this should be their Leaguepedia disambiguation name
    disambiguation: Mapped[str | None] = mapped_column(Text, unique=True)
    # We store linked IDs (GRID, RIOT_ESPORTS, Discord) in a flexible format
    external_ids = mapped_column(JSONB)
    # Debug
    updated: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    accounts: Mapped[list["Account"]] = relationship("Account", back_populates="player")

    def __repr__(self) -> str:
        if self.disambiguation is None:
            return f"{self.id}-{self.name}:{self.id}"
        return f"{self.id}-{self.name} ({self.disambiguation})"
