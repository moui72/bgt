# std imports
from pathlib import Path
import random
from datetime import datetime
from typing import List, Union, Set, Tuple, Dict
from functools import wraps

# vendor imports
from fastapi import FastAPI, HTTPException, APIRouter
from starlette.requests import Request
from pydantic import BaseModel, conint, PositiveInt

# local imports
from app.schema import Game, question_templates, Score, QID
from app._version import __version__
from app.utils import oxford_join
from app.questions import QuestionSelector, Games

routes = APIRouter()

def create_app():
    # other initialization here
    app = FastAPI()
    app.include_router(routes)
    app.state.games = Games()
        
    return app

# routes
@routes.get("/")
async def root(request: Request):
    state = request.app.state
    return {
        "version": f"v{__version__}", 
        "question_count": len(state.games.all_games) * len(question_templates)
    }

@routes.get("/questions/")
async def read_question(request: Request, asked: List[str] = None):
    "asked is a comma separated list of question ids that have been asked"
    state = request.app.state
    # memo passed between client & server ensures questions aren't repeated    
    asked_memo = set(asked.split(",") if asked is not None else ())
    qs = QuestionSelector(asked=asked_memo, games=state.games)
    return qs.nextQuestion()


@routes.post("/score/", response_model=Score)
async def create_score(score:Score):
    return score
