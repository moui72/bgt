from fastapi import FastAPI
from app.schema import (Score)
import boto3

api_version = "1.0.0"
dynamodb = boto3.resource('dynamodb')
app = FastAPI()
Games = dynamodb.Table('GamesTest')


@app.get("/")
async def root():
    return {"version": f"v{api_version}"}


@app.get("/games/{game_id}")
async def read_game(game_id: int):
    response = Games.get_item(Key={"Id": game_id})
    print(response)
    try:
        return response["Item"]
    except KeyError:
        {"detail": "Not Found"}


@app.get("/questions/{question_id}")
async def read_question(question_id: int):
    # keep a memo of questions served, so there are no repeats for a given session
    # e.g., "questions_served.append({template: 4, game_id: 45})"
    return {"question_id": question_id}


@app.post("/score/")
async def create_item(score: Score):
    return score
