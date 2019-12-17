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
    Fetched: str = datetime.now().isoformat()
    Id: int


class Game(BaseWithFetched):
    Name: str
    Developers: List[str]
    Year: int

    def toAWSDyDBScheme(self):
        return {
            "Id": {"N": str(self.id)},
            "Name": {"S": str(self.name)},
            "Year": {"N": str(self.year_published)},
            "Developers": {"S": ','.join(self.developers)}
        }

    def asPutRequest(self):
        return {
            "PutRequest": {
                "Item": self.toAWSDyDBScheme()
            }
        }


class Score(BaseWithFetched):
    Player_name: str
    Score: PositiveInt


class Question(BaseWithFetched):
    Correct_game: Game
    Alternatives: List[Game]
    Template_index: conint(ge=0, le=len(question_templates))
