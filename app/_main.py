from pathlib import Path
from fastapi import FastAPI, HTTPException
import boto3
from app.schema import *
from app._version import __version__

app = FastAPI()
dynamodb = boto3.resource('dynamodb')
games = dynamodb.Table('GamesTest')


@app.get("/")
async def root():
    return {"version": f"v{__version__}"}


@app.get("/games/")
async def read_games():
    response = games.scan()
    return response


@app.get("/games/{game_id}")
async def read_game(game_id: int):
    response = games.get_item(Key={"id": game_id})
    try:
        return response["Item"]
    except KeyError:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/questions/{question_id}")
async def read_question(question_id: int):
    # keep a memo of questions served, so there are no repeats for a given session
    # e.g., "questions_served.append({template: 4, game_id: 45})"
    return {"question_id": question_id}


@app.post("/score/")
async def create_item(score: Score):
    return score
