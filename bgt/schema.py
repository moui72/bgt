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
    fetched: datetime = datetime.now()
    id: int


class Game(BaseWithFetched):
    name: str
    developers: List[str]
    year_published: int

    def toAWSDyDBScheme(self):
        return {
            "Id": self.id,
            "Name": self.name,
            "Year": self.year_published,
            "Developers": ','.join(self.developers)
        }

    def asPutRequest(self):
        return {
            "PutRequest": {
                "Item": self.toAWSDyDBScheme()
            }
        }


class Score(BaseWithFetched):
    name: str
    score: PositiveInt


class Question(BaseWithFetched):
    correctGame: Game
    alternatives: List[Game]
    template_index: conint(ge=0, le=len(question_templates))
