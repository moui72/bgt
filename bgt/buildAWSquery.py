import json
from typing import Dict, List, Set
from decimal import Decimal
from enum import Enum
from types import GeneratorType
from boardgamegeek import BGGClient, CacheBackendSqlite
from schema import Game
from utils import oxford_join, UniversalEncoder
import datetime

with open('games.json', 'r') as jsongames:
    games = json.load(jsongames)

with open('designers.json', 'r') as jsondesigners:
    designers = json.load(jsondesigners)

validGames = [Game(**game) for game in games.values()]

query = {"Games": [game.asPutRequest() for game in validGames]}

print(query)
