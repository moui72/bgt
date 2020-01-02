# std imports
from pathlib import Path
import random
from datetime import datetime

# vendor imports
from fastapi import FastAPI, HTTPException
import boto3

# local imports
from app.schema import *
from app._version import __version__
from app.utils import oxford_join

# startup
app = FastAPI()
dynamodb = boto3.resource('dynamodb', 'us-east-1')
games = dynamodb.Table('GamesTest')
all_games = games.scan()
all_games = [Game(**g) for g in all_games["Items"]]
all_game_ids = tuple(g.id for g in all_games)
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
    # memo passed between client & server ensures questions aren't repeated    
    asked_memo = set(asked.split(",") if asked is not None else ())
    (template_index, right_game_id) = get_question_id_parts()
    new_qid = f"{template_index}-{right_game_id}"
    while new_qid in asked_memo:
        (template_index, right_game_id) = get_question_ids()
        new_qid = f"{template_index}-{right_game_id}"
    return {
        "question": Question(
            id=new_qid,
            template_index=template_index,
            correct_game=all_games_by_id[right_game_id],
            answers=get_answers(template_index,right_game_id)
        ), 
        "asked": asked
    }


@app.post("/score/")
async def create_item(player_name: str, score: int):
    return Score(player_name, score)

# helpers
def get_question_id_parts():
    template_index = random.randrange(len(question_templates))
    right_game_id = random.choice(all_game_ids)
    return template_index, right_game_id

def get_answers(template_index,right_game_id):
    template = question_templates[template_index]
    right_game = all_games_by_id[right_game_id]
    right_answer = getattr(right_game, template["answer_type"])
    answers = set()
    answers.add(oxford_join(right_answer))
    while len(answers) < 4:
        if template["answer_type"] == "year_published":
            # is the complication of code worth the extent to which this is 
            # better than sampling random games?
            alt_answer = random.randint(
                right_game.year_published-10, 
                min(datetime.now().year, right_game.year_published+10)
            )
        else:
            alt_answer = getattr(
                random.choice(all_games), 
                template["answer_type"]
            )
        answers.add(oxford_join(alt_answer))
    return list(answers)