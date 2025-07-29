from sqlalchemy import Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from .base import Base


class Champion(Base):
    __tablename__ = "champions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True)
    # alias (communitydragon) is the same as id (ddragon)
    alias: Mapped[str] = mapped_column(Text, unique=True)

    updated: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
