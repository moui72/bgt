# std
from pathlib import Path
import random

# vendor
from fastapi import FastAPI, HTTPException
import boto3

# local
from app.schema import *
from app._version import __version__

# startup
app = FastAPI()
dynamodb = boto3.resource('dynamodb', 'us-east-1')
games = dynamodb.Table('GamesTest')
all_games = games.scan()
all_games = [Game(**g) for g in all_games["Items"]]
all_game_ids = set(g.id for g in all_games)
all_games_by_id = {g.id: g for g in all_games}

# routes
@app.get("/")
async def root():
    return {"version": f"v{__version__}"}

@app.get("/games/")
def read_games(n: int = None):
    return all_games

@app.get("/games/{game_id}")
async def read_game(game_id: int):
    response = games.get_item(Key={"id": game_id})
    try:
        return Game(**response["Item"])
    except KeyError:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/questions/")
async def read_question(asked: str = None):
    "asked is a comma separated list of question ids that have been asked"
    "memo is passed back and forth between server and client to ensure "
    "questions are not repeated"
    
    asked_memo = set(asked.split(",") if asked is not None else ())
    (template_index, right_game_id) = get_question_ids()
    new_qid = f"{template_index}-{right_game_id}"
    while new_qid in asked_memo:
        (template_index, right_game_id) = get_question_ids()
        new_qid = f"{template_index}-{right_game_id}"

    return {"question_id": new_qid}


@app.post("/score/")
async def create_item(player_name: str, score: int):
    return Score(player_name, score)

# helpers
def get_question_ids():
    template_index = random.randrange(len(question_templates))
    right_game_id = random.choice(tuple(all_game_ids))
    return template_index, right_game_id

