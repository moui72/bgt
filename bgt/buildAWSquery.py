import json
from typing import Dict, List, Set
from decimal import Decimal
from enum import Enum
from types import GeneratorType
from boardgamegeek import BGGClient, CacheBackendSqlite
from schema import Game
from utils import oxford_join, UniversalEncoder
import datetime

tableName = "GamesTest"

with open('games.json', 'r') as jsongames:
    games = json.load(jsongames)

with open('designers.json', 'r') as jsondesigners:
    designers = json.load(jsondesigners)

validGames = [Game(**game) for game in games.values()]

for i in range(0, len(validGames), 25):
    query = {tableName: [game.asPutRequest() for game in validGames[i:i+25]]}
    filename = f"PutQuery{int((i/25)+1)}.json"
    with open(filename, "w") as queryfile:
        json.dump(query, queryfile, indent=2)
