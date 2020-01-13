
# Standard lib
import random
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union

# Vendor
import boto3
from fastapi import APIRouter, FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

# Relative local
from ._version import __version__
from .datatypes import (
    Answer, CSRFException, Game, Games, Question, QuestionID, Score,
    SelectedQuestion
)
from .game_mechanics import Feedback, QuestionSelector
from .utils import oxford_join

routes = APIRouter()

# routes
@routes.get("/")
async def root(request: Request) -> Dict[str, Union[str, int]]:
    games = request.app.state.games
    return {
        "version": f"v{__version__}",
        "question_count": len(games.all_qids)
    }


@routes.get("/questions/")
async def read_question(request: Request, asked: List[str] = []) \
        -> SelectedQuestion:
    "asked is a comma separated list of strings representing question ids that "
    "have been asked"
    games = request.app.state.games
    asked_memo = set(qid_from_str(a) for a in asked)
    qs = QuestionSelector(asked=asked_memo, games=games)
    q = qs.next_question()
    return {
        "question": q.question.dict(),
        "asked": q.asked
    }


@routes.post("/scores/")
async def create_score(request: Request, score: Score) -> Score:
    try:
        check_requested_with_header(request)
        put_score(score)
    except CSRFException as e:
        return HTTPException(403, detail=e)
    except Exception as e:
        raise(e)
    return score.dict()


@routes.post("/answers/")
async def check_answer(request: Request, answer: Answer) -> bool:
    games = request.app.state.games
    return Feedback(answer=answer, games=games).response()


def check_requested_with_header(r: Request):
    if "x-requested-with" not in r.headers.keys():
        raise Exception("Rejected, potential fraudulent request")
    else:
        return r

def put_score(score):
    table_name = "ScoresTest"
    dynamodb = boto3.resource('dynamodb', 'us-east-1')
    table = dynamodb.Table(table_name)
    table.put_item(Item=score.dict())
    return score


class DatabaseConnection:
    connection = None

    def __init__(self):
        self.connection = boto3.resource('dynamodb', 'us-east-1')

    def query_games(self) -> List[Game]:
        table = self.connection.Table('GamesTest')
        raw_games = table.scan()
        return [Game(**g) for g in raw_games["Items"]]


def create_app(env=None, db=None) -> FastAPI:
    db = db if db else DatabaseConnection()
    app = FastAPI()
    app.include_router(routes)
    app.state.games = Games(
        all_games=db.query_games()
    )
    origins = ["http://localhost:8080"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["GET", "POST"]
    )
    return app
