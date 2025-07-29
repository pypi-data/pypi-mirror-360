# ATG - All The Games

[![Latest Version](https://img.shields.io/pypi/v/ATG-lib?label=latest)](https://pypi.org/project/ATG-lib/)
[![Python Versions](https://img.shields.io/pypi/pyversions/ATG-lib)](https://pypi.org/project/ATG-lib/)
[![License](https://img.shields.io/github/license/Allan-Cao/ATG)](/LICENSE)

Opinionated but flexible library of database models and scripts and APIs to store solo queue / competitive games, player, team and game data tailored for LoL Esports.

## Features
- Functions to access Riot & GRID APIs with smart region handling
- SQLAlchemy database models compatible with both solo queue & esports games
- Database models to store riot game event JSONL files
- Ability to store complete Match-V5 JSON objects
- Scripts to insert/manage solo queue accounts & store new solo queue games

## 1.X Release Notes
As of version 1.X, PostgreSQL is the **required** database backend due to the use of JSONB columns which are declared using the `sqlalchemy.dialects.postgresql.JSONB` datatype.

I have decided to bump the major version since this library is mature enough for my production needs *however* expect extensive schema changes as I look to fully mature my database models.

Although naming initially reflects the match-v5 API's choices and the terminology used by GRID esports, I've had to make some changes.

Here is are the major differences / exceptions that should be noted.

| Key used | Meaning | Examples |
| --- | --- | --- |
| Series  | A collection of related games | A series has many games |
| source_data | Raw/unprocessed/additional data | Specifically in ParticipantStats we store the unprocessed match_v5 columns here |
| X_id | table_id; Foreign key name | champion_id, game_id |
| team_id  | Blue / red sides  | 100 - Blue, 200 - Red |
| participant_id | The "#" of the participant | From 1 - 10 representing blue top -> red bottom most of the time. |


## Todo
- [x] Remove the usage of `ratelimit` in favor of something that actually does stable rate limiting
- [x] Properly handle API error codes
- [x] Add the ability to store draft / other available esports game information
- [x] Open source GRID API code and GRID insertion scripts
- [ ] Handle database sessions and API keys better using dependency injection or something other than passing session objects around. I kind of like the current functional nature of the API
- [ ] Normalize database objects. Specifically the series/tournament-game relationship
- [ ] Reduce the number of nullable columns where possible. This is especially a problem on the game table
- [ ] Introduce enums where appropriate
- [ ] Transition to HTTPX > requests
- [ ] Remove or update the player_team_association table. I currently don't use it but it's definitely useful and should be revisited in the future.

## Setup & Example Usage

It is recommended to use a [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) when directly running this library's scripts.

Setup dependencies
```bash
pip install -r requirements.txt
```

Edit the .env file with your Riot API key and database connection string. The [psycopg3 database driver](https://www.psycopg.org/psycopg3/docs/basic/install.html) is installed if this code is installed as a library and is recommended.

```bash
python main.py
```

Example usage (linking a pro player by name to a solo queue account)
```python
import os
from sqlalchemy import select

from ATG.database import get_session_factory
from ATG.api import get_account_by_riot_id
from ATG.models import Player, Account

RIOT_API = os.environ["RIOT_API"]
Session = get_session_factory(os.environ["PROD_DB"])

def link_pro(pro_name, soloq):
    with Session() as session:
        try:
            player = session.execute(select(Player).where(Player.name == pro_name)).scalar_one()
        except:
            print(f"Unable to find associated player for {pro_name}")
            return
        name, tagline = soloq.split("#")
        details = get_account_by_riot_id(name, tagline, RIOT_API).json()
        new_acc = Account(puuid=details['puuid'], name=details['gameName'], tagline=details['tagLine'], region='NA1', player_id=player.id)
        session.add(new_acc)
        try:
            session.commit()
            print(f"Linked {pro_name} with {name}#{tagline}")
        except:
            session.rollback()
            print(f"Account {name}#{tagline} already linked")

link_pro("Tactical", "Tactical0#NA1")
```

## Schema changes - Alembic commands

In the case of schema changes, Alembic allows us to automatically generate a script to apply the changes to the database. When a commit will cause a schema change, an alembic script should be attached to the commit.

```bash
alembic revision --autogenerate -m "changes"
alembic upgrade head
```

## Poetry
Commands to publish updates on PyPi
```bash
poetry build
poetry publish
```

## Legal
ATG is not endorsed by Riot Games and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc
