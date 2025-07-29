from ..models import Player, Account, Participant
from sqlalchemy.orm import Session
from sqlalchemy import select

def create_player(name: str) -> Player:
    """Creates a player object

    Args:
        name (str): Player name

    Returns:
        Player: Created player object
    """
    return Player(name=name)

def create_account(puuid: str, name: str, tagline: str, player_id: int, region: str = "TOURNAMENT", skip_update: bool = True) -> Account:
    """Creates an account object

    Args:
        puuid (str): Account identifier (PUUID / Account ID)
        name (str): Account name
        tagline (str): Account tagline
        player_id (int): Player ID (foreign key)
        region (str, optional): Account region. Defaults to "TOURNAMENT".
        skip_update (bool, optional): Should be updated automatically?. Defaults to True.

    Returns:
        Account: Created account object
    """
    return Account(
        puuid=puuid,
        name=name,
        tagline=tagline,
        region=region,
        player_id=player_id,
        skip_update=skip_update)

def get_puuid(participant) -> str:
    return str(participant.get("puuid", participant["accountID"]))
def get_game_name(participant: dict) -> str | None:
    return (participant.get("riotId", {}).get("displayName") or
            participant.get("summonerName") or
            participant.get("playerName") or
            None)
def get_tagline(participant) -> str:
    return participant.get("riotId", {}).get("tagLine", "")
def get_team_id(participant) -> int:
    return participant.get("teamID", participant.get("teamId"))

def parse_game_participants(participants: list[dict], game_id: str, winning_team_id: int, NAME_ID_MAP: dict[str, int]) -> list[Participant]:
    """Parses the participants into a list of Participant objects

    Args:
        participants (list[dict]): List of game participants
        winning_team_id (int): 100 or 200 (blue/red winners)
        NAME_ID_MAP (dict[str, int]): champion name -> champion id map

    Returns:
        list[Participant]: Parsed participant objects
    """
    game_participants = []
    for participant in participants:
        game_participants.append(Participant(
            game_id = game_id,
            puuid = get_puuid(participant),
            participant_id = participant["participantID"],
            riot_id_game_name = get_game_name(participant),
            riot_id_tagline = get_tagline(participant),
            summoner_id = participant["accountID"],
            team_id = get_team_id(participant),
            champion_id = NAME_ID_MAP[participant["championName"].lower()],
            win = get_team_id(participant) == winning_team_id,
        ))
    return game_participants

def get_common_prefix_length(player_names: list[str]) -> int:
    """Gets the number of charaters shared in the prefix of all items of a list

    Args:
        player_names (list[str]): A list of player names

    Returns:
        int: The length of the shared prefix
    """
    common_prefix_length = 0
    for chars in zip(*player_names):
        if len(set(chars)) == 1:
            common_prefix_length += 1
        else:
            break
    return common_prefix_length

def create_missing_accounts(session: Session, participants: dict):
    """Helper function to parse a list of participants and add to the session any missing players/accounts.

    Args:
        session (Session): Active SQLAlchemy session object
        participants (dict): A match-v5 like participant list
    """
    stored_puuids = session.scalars(select(Account.puuid)).all()
    for participant in participants:
        puuid = get_puuid(participant)
        if puuid not in stored_puuids:
            game_name = get_game_name(participant)
            player_names = [get_game_name(p) for p in participants if get_team_id(p) == get_team_id(participant)]
            player_name = game_name[get_common_prefix_length(player_names):]

            db_player = session.scalar(select(Player).where(Player.name == player_name))

            if db_player is None:
                db_player = create_player(player_name)
                session.add(db_player)
                session.flush()

            session.add(create_account(puuid, game_name, get_tagline(participant), db_player.id))
