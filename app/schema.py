#std
from datetime import datetime

# vendor
from pydantic import BaseModel, conint, PositiveInt
from typing import List, Union, Set, Tuple

#local


question_templates: List[dict] = [
    {
        "text": lambda a: f"Who designed {a}?",
        "answer_type": "developers",
        "question_type": "name"
    },
    {
        "text": lambda a: f"When was {a} released?",
        "answer_type": "year",
        "question_type": "name"
    },
    {
        "text": lambda a: f"Which game was designed by {a}?",
        "answer_type": "name",
        "question_type": "design"
    },
    {
        "text": lambda a: f"Which game came out in {a}?",
        "answer_type": "name",
        "question_type": "year"
    },
]


class BaseWithFetched(BaseModel):
    fetched: str = datetime.now().isoformat()
    id: int


class Game(BaseWithFetched):
    name: str
    developers: List[str]
    year: int

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return dict(self) == dict(other)

    def toAWSDyDBScheme(self):
        return {
            "id": {"N": str(self.id)},
            "name": {"S": str(self.name)},
            "year": {"N": str(self.year)},
            "developers": {"S": ','.join(self.developers)}
        }


class Score(BaseWithFetched):
    player_name: str
    score: PositiveInt

class QID(BaseModel):
    right_game: int
    template_index: conint(ge=0, le=len(question_templates))

    def template(self):
        return question_templates[self.template_index]

    def __str__(self):
        return f"{self.template_index}-{self.right_game}"
    
    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, other):
        return str(self) == str(other)

class Question(BaseModel):
    id: QID
    text: str
    answers: List[Union[str,int]]

def qid_from_str(qid_str: str):
    temp = qid_str.split("-")
    return QID(template_index=temp[0], right_game=temp[1])