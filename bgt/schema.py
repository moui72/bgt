#std
from datetime import datetime

# vendor
from pydantic import BaseModel, conint, PositiveInt
from typing import List, Union, Set, Tuple, Callable, Dict

#local


question_templates: List[Dict[str,Union[str,Callable[[str],str]]]] = [
    {
        "text": lambda a: f'Who was &ldquo;{a}&rdquo; designed by?',
        "answer_type": "developers",
        "question_type": "name"
    },
    {
        "text": lambda a: f'What year was &ldquo;{a}&rdquo; released?',
        "answer_type": "year",
        "question_type": "name"
    },
    {
        "text": lambda a: f"Which game was designed by {a}?",
        "answer_type": "name",
        "question_type": "developers"
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

    class Config:
        allow_population_by_field_name = True
        fields = {"year": "year_published"}


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

    def template(self) -> Dict[str,Union[str,Callable[[str],str]]]:
        return question_templates[self.template_index]

    def __str__(self) -> str:
        return f"{self.template_index}-{self.right_game}"
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, other) -> bool:
        return str(self) == str(other)

class Question(BaseModel):
    id: QID
    text: str
    answers: List[Union[str,int]]


class SelectedQuestion(BaseModel):
    question: Question
    asked: Set[QID]


class Answer(BaseModel):
    question: Question
    answer: str

    def template(self) -> Dict[str,Union[str,Callable[[str],str]]]:
        return question_templates[self.question.template_index]
    
    def correct(self) -> bool:
        pass

class Feedback(BaseModel):
    answer: Answer


# helpers
def qid_from_str(qid_str: str) -> QID:
    temp = qid_str.split("-")
    return QID(template_index=temp[0], right_game=temp[1])

