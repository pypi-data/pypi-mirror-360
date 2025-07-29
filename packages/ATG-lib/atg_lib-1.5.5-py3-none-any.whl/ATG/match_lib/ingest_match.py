from datetime import datetime, timedelta
from sqlalchemy import and_, select
from sqlalchemy.orm import Session as _Session
from tqdm import tqdm
from ..api import get_match_history, get_match_by_id
from ..api.account_v1 import get_account_by_puuid
from ..models import Player, Game, Participant, Account, TeamDto, ParticipantStat
from ..utils import SEASON_START, snake_to_camel


def update_account_names(session: _Session, API_KEY: str, days: int = 7):
    """Updates player account names/taglines"""
    update_delta = datetime.now() - timedelta(days=days)
    accounts_to_update = list(
        session.scalars(
            select(Account).where(
                and_(
                    Account.updated < update_delta,
                    Account.solo_queue_account == True,
                    Account.skip_update == False,
                )
            )
        )
    )
    if len(accounts_to_update) == 0:
        print("All accounts are up to date!")
        return
    for account in tqdm(accounts_to_update):
        account_details = get_account_by_puuid(account.puuid, API_KEY)
        account_details = account_details.json()
        account.name = account_details["gameName"]
        account.tagline = account_details["tagLine"]
        account.updated = datetime.now()
    try:
        session.commit()
    except Exception as e:
        print(f"Something went wrong updating accounts: {str(e)}")
        session.rollback()


def insert_match_history(
    session: _Session,
    player: Player,
    API_KEY: str,
    start_time: int = SEASON_START,
    start_latest: bool = True,
    queue_id: int = 420,
):
    existing_ids = set(session.scalars(select(Game.id)).all())
    for account in player.accounts or []:
        if not account.solo_queue_account or account.skip_update:
            continue
        print(f"Updating match history for {str(account)}")

        if start_latest:
            latest_game_timestamp = session.scalar(
                select(Game.game_end_timestamp)
                .join(Participant, Participant.game_id == Game.id)
                .where(
                    and_(Participant.puuid == account.puuid, Game.queue_id == queue_id)
                )
                .order_by(Game.game_end_timestamp.desc())
                .limit(1)
            )
            if latest_game_timestamp is None:
                start_time = SEASON_START
            else:
                start_time = int(latest_game_timestamp.timestamp())
        match_ids = get_match_history(
            account.puuid,
            account.region,
            API_KEY,
            startTime=start_time,
            queue=queue_id,
        )
        new_match_ids = set(match_ids) - existing_ids

        if len(new_match_ids) == 0:
            print("All up to date!")
            continue

        for match_id in tqdm(new_match_ids):
            try:
                game_data = get_match_by_id(match_id, API_KEY).json()["info"]
                process_match(session, match_id, game_data)
                existing_ids.add(match_id)
            except Exception as e:
                print(f"Failed to process match {match_id}: {str(e)}")
        session.commit()


def process_match(
    session: _Session,
    game_id: str,
    game_data: dict,
    game_args: dict = {},
) -> int | None:
    """Function to process game data from MatchV5-like sources. If the game already exists, processing will be skipped.

    Args:
        session: ORM Session object
        game_id: Riot's Game ID number
        match_data: MatchV5-like Dictionary to be processed
        game_args: Additional fields to be passed to the game object
    """
    if session.query(Game).filter(Game.id == game_id).one_or_none() is not None:
        return

    if len(game_data.get("participants", [])) > 0:
        early_surrender = game_data["participants"][0].get(
            "gameEndedInEarlySurrender", False
        )
        surrender = game_data["participants"][0].get("gameEndedInSurrender", False)
    else:
        early_surrender = False
        surrender = False

    game = Game(
        **{k: game_data.get(snake_to_camel(k)) for k in Game.INFO_DTO},
        **{k: datetime.fromtimestamp(game_data[snake_to_camel(k)] / 1000) for k in Game.TIMESTAMPS},
        **{"id": game_id},
        **game_args,
        game_ended_in_early_surrender=early_surrender,
        game_ended_in_surrender=surrender,
    )

    session.add(game)
    session.flush() # We need to flush to ensure the game id exists in the database.

    for team in game_data["teams"]:
        teamDto = TeamDto(
            game_id=game.id,
            bans=team["bans"],
            objectives=team["objectives"],
            team_id=team["teamId"],
            win=team["win"],
        )
        session.add(teamDto)

    # For some reason, zero duration game's are permitted by GRID. We can not process the match data for these games
    if game.game_duration and game.game_duration > 0:
        participant_stats = []
        game_participants = game_data["participants"]
        for participant in game_participants:
            # First we extract the columns defined in the model and the DTOs we're storing
            participant_dto_extraction = {
                k: participant[snake_to_camel(k)] for k in Participant.PARTICIPANT_DTO
            }
            participant_stat_extraction = {
                k: participant[snake_to_camel(k)]
                for k in ParticipantStat.PARTICIPANT_STAT_DTO
            }

            # Handle special fields that require extra processing
            special_fields = {}
            special_fields["perks"] = participant.get("perks")
            special_fields["total_time_CC_dealt"] = int(participant.get("totalTimeCCDealt", 0))
            special_fields["time_CC_ing_others"] = int(participant.get("timeCCingOthers", 0))
            special_fields["total_gold"] = int(participant.get("goldEarned", 0))
            special_fields["current_gold"] = int(participant.get("goldEarned", 0) - participant.get("goldSpent", 0))

            source_data = dict(participant)

            keys_to_remove = (
                ParticipantStat.PARTICIPANT_STAT_DTO +
                Participant.PARTICIPANT_DTO +
                ["perks", "totalTimeCCDealt", "timeCCingOthers", "goldEarned", "goldSpent"]
            )
            for key in keys_to_remove:
                camel_key = snake_to_camel(key) if key in ParticipantStat.PARTICIPANT_STAT_DTO + Participant.PARTICIPANT_DTO else key
                source_data.pop(camel_key, None)

            new_participant = Participant(game_id=game.id, **participant_dto_extraction)
            session.add(new_participant)
            session.flush()
            participant_stats.append(
                ParticipantStat(
                    participant_id=new_participant.id,
                    **participant_stat_extraction,
                    **special_fields,
                    source_data=source_data,
                )
            )

        session.add_all(participant_stats)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Something went wrong ingesting match {game_id}: {str(e)}")
