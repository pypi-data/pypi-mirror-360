import requests as r
from requests import Response
from .utils import headers, RoutingLiteral
from ..rate_limiter import riot_api_limiter


@riot_api_limiter(endpoint_key="account_v1_by_riot_id")
def get_account_by_riot_id(
    game_name: str, tag_line: str, api_key: str, routing: RoutingLiteral = "americas"
) -> Response:
    _headers = {"X-Riot-Token": api_key, **headers}
    # There are three routing values for account-v1; americas, asia, and europe. You can query for any account in any region. We recommend using the nearest cluster.
    response = r.get(
        f"https://{routing}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}",
        headers=_headers,
    )
    return response


@riot_api_limiter(endpoint_key="account_v1_by_puuid")
def get_account_by_puuid(
    puuid: str, api_key: str, routing: RoutingLiteral = "americas"
) -> Response:
    _headers = {"X-Riot-Token": api_key, **headers}
    response = r.get(
        f"https://{routing}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}",
        headers=_headers,
    )
    return response
