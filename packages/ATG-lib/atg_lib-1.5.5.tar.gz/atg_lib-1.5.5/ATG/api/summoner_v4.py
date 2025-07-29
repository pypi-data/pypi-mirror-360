import requests as r
from requests import Response
from .utils import headers, RegionLiteral
from ..rate_limiter import riot_api_limiter


@riot_api_limiter(endpoint_key="summoner_v4_by_account_id")
def get_summoner_by_account_id(
    account_id: str, region: RegionLiteral, api_key: str, **kwargs
) -> Response:
    _headers = {"X-Riot-Token": api_key, **headers}
    response = r.get(
        f"https://{region.lower()}.api.riotgames.com/lol/summoner/v4/summoners/by-account/{account_id}",
        headers=_headers,
        params=kwargs,
    )
    return response


@riot_api_limiter(endpoint_key="summoner_v4_by_puuid")
def get_summoner_by_puuid(
    puuid: str, region: RegionLiteral, api_key: str, **kwargs
) -> Response:
    _headers = {"X-Riot-Token": api_key, **headers}
    response = r.get(
        f"https://{region.lower()}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}",
        headers=_headers,
        params=kwargs,
    )
    return response


@riot_api_limiter(endpoint_key="summoner_v4_by_summoner_id")
def get_summoner_by_summoner_id(
    summoner_id: str, region: RegionLiteral, api_key: str, **kwargs
) -> Response:
    _headers = {"X-Riot-Token": api_key, **headers}
    response = r.get(
        f"https://{region.lower()}.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}",
        headers=_headers,
        params=kwargs,
    )
    return response
