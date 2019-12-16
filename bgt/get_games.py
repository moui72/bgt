import json
from typing import Dict, Set
from boardgamegeek import BGGClient, CacheBackendSqlite
from schema import Game
from utils import oxford_join, UniversalEncoder


validGames: Dict[str, Game] = {}
validDesigners: Set[str] = set()
bgg = BGGClient(cache=CacheBackendSqlite(path="cache.db", ttl=3600))

collection = bgg.collection("xelissa")
ids = [game.id for game in collection.items]
hotness = bgg.hot_items("boardgame")
ids += [game.id for game in hotness.items]

for i in range(0, len(ids), 50):
    games = bgg.game_list(ids[i:i+50])
    for game in games:
        if not game.expansion:
            for designer in game.designers:
                validDesigners.add(designer)
            try:
                validatedGame = Game(
                    name=game.name,
                    year_published=game.year,
                    bgg_game_id=game.id,
                    developers=game.designers,
                    id=game.id
                )
                validGames[str(validatedGame.id)] = validatedGame
            except Exception as e:
                print(e)

print(f"Added {len(validGames.keys())} games")
print(f"Added {len(validDesigners)} designers")
sort(validDesigners)

with open('games.json', 'w+') as jsongames:
    json.dump(validGames, jsongames, cls=UniversalEncoder, indent=2)

with open('designers.json', 'w+') as jsondesigners:
    json.dump(validDesigners, jsondesigners, cls=UniversalEncoder, indent=2)
