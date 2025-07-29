from datetime import timedelta
from enum import Enum, StrEnum, auto

DEFAULT_REGION = "NA"
SEASON_START = 1736420400  # Season 15. Season 14 was 1704884400
MINIMUM_MATCH_DURATION = timedelta(minutes=10)

class SeriesType(StrEnum):
    """Enum to represent how the series types are represented in the GRID API
    
    This originally was found in central_data.enums's SeriesType"""
    COMPETITIVE = auto()
    ESPORTS = auto()
    LOOPFEED = auto()
    SCRIM = auto()

class SeriesStatus(StrEnum):
    """Enum to represent many of the possible states that an esports series may be in.
    
    Probably won't use all of them immediately but this should serve as a pretty good basis.
    """
    ###    Pre-game states    ###
    SCHEDULED = auto()          # Series is scheduled but hasn't started yet   
    CANCELLED = auto()          # Series was cancelled
    
    ###   During-game states  ###
    IN_PROGRESS = auto()        # Series is currently being played
    PAUSED = auto()             # Series is temporarily paused (technical issues, etc.)
    
    ###    Post-game states   ###
    PENDING_PROCESSING = auto() # Series complete, waiting for processing
    PROCESSING = auto()         # Currently being processed (processing lock)
    PARTIAL = auto()            # Some games ingested successfully, others missing
    INCOMPLETE = auto()         # Some data is missing (players, events, etc.)
    
    ###      Final states     ###
    VALID = auto()              # All games and data are ingested and valid
    FAILED = auto()             # Processing failed completely, needs retry
    BUGGED = auto()             # Data exists but has inconsistencies/errors or failed on retry
    
    ###      Special cases    ###
    NO_DATA_AVAILABLE = auto()  # Series exists in GRID but no game data available
    NEEDS_REVIEW = auto()       # Flagged for manual review
    

class Side(Enum):
    blue = 100
    red = 200


class Lane(Enum):
    TOP = "top_lane"
    JNG = "jungle"
    MID = "mid_lane"
    BOT = "bot_lane"
    SUP = "utility"


class TeamPosition(Enum):
    AFK = None
    BOTTOM = "BOT"
    JUNGLE = "JNG"
    MIDDLE = "MID"
    TOP = "TOP"
    UTILITY = "SUP"
