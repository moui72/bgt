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
from .schema import (
    Game, question_templates, Score, QID, Question, Feedback, Answer
)
from ._version import __version__
from .utils import oxford_join
from .questions import QuestionSelector, SelectedQuestion, Games

routes = APIRouter()

def create_app(env = None) -> FastAPI:
    # other initialization here
    app = FastAPI()
    app.include_router(routes)
    app.state.games = Games(games=query_games())
    return app

def query_games() -> List[Game]:
    dynamodb = boto3.resource('dynamodb', 'us-east-1')
    table = dynamodb.Table('GamesTest')
    raw_games = table.scan()
    return [Game(**g) for g in raw_games["Items"]]

# routes
@routes.get("/")
async def root(request: Request) -> Dict[str,Union[str,int]]:
    state = request.app.state
    return {
        "version": f"v{__version__}", 
        "question_count": len(state.games.all_qids)
    }

@routes.get("/questions/")
async def read_question(request: Request, asked: List[str] = []) \
    -> SelectedQuestion:
    "asked is a comma separated list of strings representing question ids that "
    "have been asked"
    state = request.app.state
    asked_memo = set(qid_from_str(a) for a in asked)
    qs = QuestionSelector(asked=asked_memo, games=state.games)
    q = qs.next_question()
    return {
        "question": q.question.dict(),
        "asked": q.asked
    }


@routes.post("/score/", response_model=Score)
async def create_score(score:Score) -> Score:
    return score

@routes.post("/check_answer/", response_model=Feedback)
async def check_answer(answer: Answer) -> Feedback:
    return Feedback(answer)
