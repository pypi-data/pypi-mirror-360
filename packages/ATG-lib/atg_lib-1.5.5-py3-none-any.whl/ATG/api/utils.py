from typing import Dict, Literal
from enum import StrEnum

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en-CA;q=0.9,en;q=0.8,ru-RU;q=0.7,ru;q=0.6,ko-KR;q=0.5,ko;q=0.4",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
}

# The AMERICAS routing value serves NA, BR, LAN and LAS. The ASIA routing value serves KR and JP. The EUROPE routing value serves EUNE, EUW, ME1, TR and RU. The SEA routing value serves OCE, SG2, TW2 and VN2.
PLATFORM_ROUTING: Dict[str, str] = {
    "NA1": "americas",
    "BR1": "americas",
    "LA1": "americas",
    "LA2": "americas",
    "KR": "asia",
    "JP": "asia",
    "ME1": "europe",
    "EUN1": "europe",
    "EUW1": "europe",
    "TR1": "europe",
    "RU": "europe",
    "OC1": "sea",
    "SG2": "sea",
    "TW2": "sea",
    "VN2": "sea",
}

RoutingLiteral = Literal["americas", "asia", "europe", "sea"]
RegionLiteral = Literal[
    "NA1",
    "BR1",
    "LA1",
    "LA2",
    "KR",
    "JP",
    "ME1",
    "EUN1",
    "EUW1",
    "TR1",
    "RU",
    "OC1",
    "SG2",
    "TW2",
    "VN2",
]
QueueLiteral = Literal["RANKED_SOLO_5x5", "RANKED_FLEX_SR", "RANKED_FLEX_TT"]
DivisionLiteral = Literal["I", "II", "III", "IV"]
TierLiteral = Literal[
    "DIAMOND", "EMERALD", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"
]

REGIONS = StrEnum("Regions", [(_, _) for _ in PLATFORM_ROUTING.keys()])
QUEUES = StrEnum(
    "Queues", [(_, _) for _ in ["RANKED_SOLO_5x5", "RANKED_FLEX_SR", "RANKED_FLEX_TT"]]
)
DIVISIONS = StrEnum("Divisions", [(_, _) for _ in ["I", "II", "III", "IV"]])
TIERS = StrEnum(
    "Tiers",
    [
        (_, _)
        for _ in ["DIAMOND", "EMERALD", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"]
    ],
)


def parse_match_id(match_id: str) -> tuple[str, str]:
    split = match_id.split("_")
    if len(split) != 2:
        raise ValueError(f"Unable to parse {match_id}")
    if split[0] not in REGIONS:
        raise ValueError(f"Unknown region {split[0]} received")
    return split[0], split[1]
