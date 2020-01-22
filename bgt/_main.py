
# Standard lib
import random
from datetime import datetime
from functools import wraps
from operator import attrgetter
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

# Vendor
import boto3
from boto3.resources.base import ServiceResource
from fastapi import APIRouter, FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

# Relative local
from ._version import __version__
from .datatypes import (
    Answer, CSRFException, Game, Games, Question, QuestionID, Score,
    SelectedQuestion, QuestionID
)
from .game_mechanics import Feedback, QuestionSelector
from .utils import oxford_join


class DatabaseConnection:
    connection: ServiceResource = None
    games_table_name: str = "GamesTest"
    scores_table_name: str = "ScoresTest"

    def __init__(self):
        self.connection = boto3.resource('dynamodb', 'us-east-1')

    def _get_table(self, table_name):
        return self.connection.Table(table_name)

    def get_games(self) -> List[Game]:
        table = self._get_table(self.games_table_name)
        raw_games = table.scan()
        return [Game(**g) for g in raw_games["Items"]]

    def put_score(self, score: Score):
        table = self._get_table(self.scores_table_name)
        table.put_item(Item=score.dict())
        return score

    def get_scores(self, n: Optional[int] = None):
        table = self._get_table(self.scores_table_name)
        raw_scores = table.scan()
        scores = [Score(**s) for s in raw_scores["Items"]]
        sorted_scores = sorted(scores, key=attrgetter('score'), reverse=True)
        return sorted_scores[:n]


routes = APIRouter()


def create_app(db: DatabaseConnection = None) -> FastAPI:
    # app setup
    app = FastAPI()
    app.include_router(routes)
    db = db or DatabaseConnection()
    app.state.db = db
    app.state.games = Games(all_games=db.get_games())
    # CORS config
    origins = ["http://localhost:8080"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["GET", "POST"]
    )
    # app is ready!
    return app


def check_csrf(r: Request):
    if "x-requested-with" not in r.headers.keys():
        raise CSRFException(args=["Rejected, potential fraudulent request "
                                  "(missing 'x-requested-with' header)"])
    if ("origin" not in r.headers.keys() or
            r.headers['origin'] not in ["http://localhost:8080"]):
        o = r.headers['origin']
        raise CSRFException(args=[f"Rejected, potential fraudulent request "
                                  f"(illegal origin {o})"])
    return r

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
    "asked represents question ids that have been asked in the current game"
    games = request.app.state.games
    asked_memo = set(QuestionID.from_str(a) for a in asked)
    qs = QuestionSelector(asked=asked_memo, games=games)
    q = qs.next_question()
    return {
        "question": q.question.dict(),
        "asked": q.asked
    }


@routes.post("/scores/")
async def create_score(request: Request, score: Score) -> Dict:
    db = request.app.state.db
    try:
        check_csrf(request)
        db.put_score(score)
    except CSRFException as e:
        raise HTTPException(403, detail=e.args)
    except Exception as e:
        raise e
    return score.dict()


@routes.get("/scores/")
async def get_scores(request: Request, n: int = 10) -> List[Score]:
    db = request.app.state.db
    scores = db.get_scores(n)
    return scores


@routes.post("/answers/")
async def check_answer(request: Request, answer: Answer) -> bool:
    games = request.app.state.games
    return Feedback(answer=answer, games=games).response()
