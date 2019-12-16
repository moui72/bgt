from fastapi import FastAPI
from schema import (Score)

api_version = 1
app = FastAPI()


@app.get("/")
async def root():
    return {"version": f"v{api_version}"}


@app.get("/games/{game_id}")
async def read_game(game_id: int):
    return {"game_id": game_id}


@app.get("/questions/{question_id}")
async def read_question(question_id: int):
    # keep a memo of questions served, so there are no repeats for a given session
    # e.g., "questions_served.push({template: 4, game_id: 45})"
    return {"question_id": question_id}


@app.post("/score/")
async def create_item(score: Score):
    return score
