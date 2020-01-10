
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
from .game_mechanics import Feedback, QuestionSelector
from .datatypes import (
    Answer, Game, Games, Question, QuestionID, Score,
    SelectedQuestion
)
from .utils import oxford_join

routes = APIRouter()


def create_app(env=None) -> FastAPI:
    # other initialization here
    app = FastAPI()
    app.include_router(routes)
    app.state.games = Games(all_games=query_games())
    origins = ["http://localhost:8080"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["GET", "POST"]
    )
    return app


def query_games() -> List[Game]:
    dynamodb = boto3.resource('dynamodb', 'us-east-1')
    table = dynamodb.Table('GamesTest')
    raw_games = table.scan()
    return [Game(**g) for g in raw_games["Items"]]

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


@routes.post("/score/", response_model=Score)
async def create_score(request: Request, score: Score) -> Score:
    try:
        check_requested_with_header(request)
    except CSRFException as e:
        return HTTPException(403, detail=e)
    return score


@routes.post("/answers/")
async def check_answer(request: Request, answer: Answer) -> bool:
    games = request.app.state.games
    return Feedback(answer=answer, games=games).response()


def check_requested_with_header(r: Request):
    if "x-requested-with" not in r.headers.keys():
        raise Exception("Rejected, potential fraudulent request")
    else:
        return request.headers["x-requested-with"]


class CSRFException(Exception):
    def __init__(self, args):
        self.args = args
