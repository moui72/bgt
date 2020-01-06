# std imports
import random
from pathlib import Path
from datetime import datetime
from typing import List, Union, Set, Tuple, Dict
from functools import wraps

# vendor imports
import boto3
from fastapi import FastAPI, HTTPException, APIRouter
from starlette.requests import Request
from pydantic import BaseModel, conint, PositiveInt


# local imports
from app.schema import Game, question_templates, Score, QID
from app._version import __version__
from app.utils import oxford_join
from app.questions import Question_Selector, Games

routes = APIRouter()

def create_app():
    # other initialization here
    app = FastAPI()
    app.include_router(routes)
    app.state.games = Games(games=query_games())
    return app

def query_games():
    dynamodb = boto3.resource('dynamodb', 'us-east-1')
    table = dynamodb.Table('GamesTest')
    raw_games = table.scan()
    return [Game(**g) for g in raw_games["Items"]]

# routes
@routes.get("/")
async def root(request: Request):
    state = request.app.state
    return {
        "version": f"v{__version__}", 
        "question_count": len(state.games.all_qids)
    }

@routes.get("/questions/")
async def read_question(request: Request, asked: List[str] = None):
    "asked is a comma separated list of question ids that have been asked"
    state = request.app.state
    # memo passed between client & server ensures questions aren't repeated    
    asked_memo = set(asked.split(",") if asked is not None else ())
    qs = Question_Selector(asked=asked_memo, games=state.games)
    return qs.nextQuestion()


@routes.post("/score/", response_model=Score)
async def create_score(score:Score):
    return score
