from pydantic import (BaseModel, conint, PositiveInt)
from typing import List
from datetime import datetime

question_templates: List[dict] = [
    {
        "text": "Who designed >>name<<?",
        "answer_type": ">>designer<<"
    },
    {
        "text": "When was >>name<< released?",
        "answer_type": ">>year_published<<"
    },

    {
        "text": "Which game was designed by >>designer<<?",
        "answer_type": ">>name<<"
    },

    {
        "text": "Which game came out in >>year_published<<?",
        "answer_type": ">>name<<"
    },
]


class BaseWithFetched(BaseModel):
    fetched: str = datetime.now().isoformat()
    id: int


class Game(BaseWithFetched):
    name: str
    developers: List[str]
    year_published: int

    def toAWSDyDBScheme(self):
        return {
            "id": {"N": str(self.id)},
            "name": {"S": str(self.name)},
            "year": {"N": str(self.year_published)},
            "developers": {"S": ','.join(self.developers)}
        }

    def asPutRequest(self):
        return {
            "PutRequest": {
                "Item": self.toAWSDyDBScheme()
            }
        }


class Score(BaseWithFetched):
    player_name: str
    score: PositiveInt


class Question(BaseWithFetched):
    correct_game: Game
    alternatives: List[Game]
    template_index: conint(ge=0, le=len(question_templates))
