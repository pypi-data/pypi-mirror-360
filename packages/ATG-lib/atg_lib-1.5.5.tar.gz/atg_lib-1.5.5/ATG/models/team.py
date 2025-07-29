from sqlalchemy import Text, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from .base import Base
from .player_team_association import PlayerTeamAssociation


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    # Multiple teams can share the same name in the GRID and LoL Esports APIs
    name: Mapped[str] = mapped_column(Text, unique=False)
    # Multiple teams can share the same team code due to inconsistancies in GRID/Bayes data e.x. academy teams share team codes with their main team
    team_code: Mapped[str | None] = mapped_column(Text, unique=False, nullable=True)

    # We store additional information in a JSONB blob
    source_data = mapped_column(JSONB)

    # Debug
    updated: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    player_associations: Mapped[list["PlayerTeamAssociation"]] = relationship(
        "PlayerTeamAssociation", back_populates="team"
    )

    def __repr__(self):
        return f"<Team(id='{self.id}', code='{self.name}')>"
