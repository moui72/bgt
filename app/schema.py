#std
from datetime import datetime

# vendor
from pydantic import BaseModel, conint, PositiveInt
from typing import List, Union

#local


question_templates: List[dict] = [
    {
        "text": lambda g: f"Who designed {g.name}?",
        "answer_type": "developers",
        "category": "design"
    },
    {
        "text": lambda g: f"When was {g.name} released?",
        "answer_type": "year_published",
        "category": "year"
    },
    {
        "text": lambda g: f"Which game was designed by {g.devs()}?",
        "answer_type": "name",
        "category": "design"
    },
    {
        "text": lambda g: f"Which game came out in {g.year_published}?",
        "answer_type": "name",
        "category": "year"
    },
]


class BaseWithFetched(BaseModel):
    fetched: str = datetime.now().isoformat()
    id: int


class Game(BaseWithFetched):
    name: str
    developers: List[str]
    year_published: int

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

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

    def devs(self):
        items = self.developers
        if len(items) == 1:
            return items[0]
        oxford_comma = (",","")[len(items) == 2]
        return ', '.join(items[:-1]) + f'{oxford_comma} and  {items[-1]}'


class Score(BaseWithFetched):
    player_name: str
    score: PositiveInt


class Question(BaseModel):
    id: str
    template_index: conint(ge=0, le=len(question_templates))
    text: str
    answers: List[Union[str,int]]
