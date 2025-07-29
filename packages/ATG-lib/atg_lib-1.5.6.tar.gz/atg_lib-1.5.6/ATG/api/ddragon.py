import requests as r
from requests import Response


def get_ddragon_versions() -> Response:
    return r.get("https://ddragon.leagueoflegends.com/api/versions.json")
