from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base


class PlayerTeamAssociation(Base):
    __tablename__ = "player_team_associations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"))
    team_id: Mapped[str] = mapped_column(Text, ForeignKey("teams.id"))
    # Although not explicitly enforced, the (TOP, JUNGLE, MIDDLE, BOTTOM, UTILITY) is generally used
    position: Mapped[str | None] = mapped_column(Text, nullable=True)

    team: Mapped["Team"] = relationship("Team", back_populates="player_associations")

    def __repr__(self):
        return f"<PlayerTeamAssociation(id='{self.id}', player_id='{self.player_id}', team_id='{self.team_id}', position='{self.position}')>"
