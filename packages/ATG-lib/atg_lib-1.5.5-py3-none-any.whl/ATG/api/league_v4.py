import requests as r
from requests import Response
from .utils import headers, RegionLiteral, QueueLiteral, DivisionLiteral, TierLiteral
from ..rate_limiter import riot_api_limiter


@riot_api_limiter(endpoint_key="league_v4_get_challengers")
def get_challengers(
    region: RegionLiteral, queue: QueueLiteral, api_key: str
) -> Response:
    _headers = {"X-Riot-Token": api_key, **headers}
    response = r.get(
        f"https://{region.lower()}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/{queue}",
        headers=_headers,
    )
    return response


@riot_api_limiter(endpoint_key="league_v4_get_grandmasters")
def get_grandmasters(
    region: RegionLiteral, queue: QueueLiteral, api_key: str
) -> Response:
    _headers = {"X-Riot-Token": api_key, **headers}
    response = r.get(
        f"https://{region.lower()}.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/{queue}",
        headers=_headers,
    )
    return response


@riot_api_limiter(endpoint_key="league_v4_get_masters")
def get_masters(region: RegionLiteral, queue: QueueLiteral, api_key: str) -> Response:
    _headers = {"X-Riot-Token": api_key, **headers}
    response = r.get(
        f"https://{region.lower()}.api.riotgames.com/lol/league/v4/masterleagues/by-queue/{queue}",
        headers=_headers,
    )
    return response


@riot_api_limiter(endpoint_key="league_v4_entries_puuid")
def get_league_entries_by_puuid(
    region: RegionLiteral, puuid: str, api_key: str
) -> Response:
    _headers = {"X-Riot-Token": api_key, **headers}
    response = r.get(
        f"https://{region.lower()}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}",
        headers=_headers,
    )
    return response


@riot_api_limiter(endpoint_key="league_v4_entries_summoner_id")
def get_league_entries_by_summoner_id(
    region: RegionLiteral, summoner_id: str, api_key: str
) -> Response:
    _headers = {"X-Riot-Token": api_key, **headers}
    response = r.get(
        f"https://{region.lower()}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}",
        headers=_headers,
    )
    return response


@riot_api_limiter(endpoint_key="league_v4_all_entries")
def get_all_league_entries(
    region: RegionLiteral,
    queue: QueueLiteral,
    tier: TierLiteral,
    division: DivisionLiteral,
    api_key: str,
    page: int = 1,
) -> Response:
    _headers = {"X-Riot-Token": api_key, "page": str(page), **headers}
    response = r.get(
        f"https://{region.lower()}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}",
        headers=_headers,
    )
    return response


@riot_api_limiter(endpoint_key="league_v4_entries_league_id")
def get_league_entries_by_league_id(
    region: RegionLiteral, league_id: str, api_key: str
) -> Response:
    _headers = {"X-Riot-Token": api_key, **headers}
    response = r.get(
        f"https://{region.lower()}.api.riotgames.com/lol/league/v4/leagues/{league_id}",
        headers=_headers,
    )
    return response
