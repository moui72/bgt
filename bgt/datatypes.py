# Standard lib
from datetime import datetime
from typing import Callable, Dict, List, Set, Tuple, Union

# Vendor
from pydantic import BaseModel, PositiveInt, conint, validator

QUESTION_TEMPLATES: List[Dict[str, Union[str, Callable[[str], str]]]] = [
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


class Score(BaseModel):
    name: str
    score: int
    id: str = None
    fetched: str = datetime.now().isoformat()

    @validator('id', always=True)
    def derive_id(cls, v, values):
        name = values["name"]
        if "id" in values.keys() and values["id"] is not None:
            return values["id"]
        else:
            f"{name}-{datetime.now().timestamp()}"


class QuestionID(BaseModel):
    right_game: int
    template_index: conint(ge=0, le=len(QUESTION_TEMPLATES))

    def template(self) -> Dict[str, Union[str, Callable[[str], str]]]:
        return QUESTION_TEMPLATES[self.template_index]

    def __str__(self) -> str:
        return f"{self.template_index}-{self.right_game}"

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    @classmethod
    def from_str(cls, qid_str: str):
        index, game = qid_str.split("-")
        return QuestionID(template_index=index, right_game=game)


class Games(BaseModel):
    all_games: List[Game]
    all_games_by_id: Dict[int, Game] = None
    all_game_ids: Tuple[PositiveInt] = None
    all_qids: Set[QuestionID] = None

    @validator('all_games_by_id', always=True)
    def derive_games_by_id(cls, v, values):
        return {g.id: g for g in values['all_games']}

    @validator('all_game_ids', always=True)
    def derive_game_ids(cls, v, values):
        return values["all_games_by_id"].keys()

    @validator('all_qids', always=True)
    def derive_qids(cls, v, values):
        return set(
            QuestionID(template_index=template_index, right_game=game_id)
            for template_index in range(len(QUESTION_TEMPLATES))
            for game_id in values["all_game_ids"]
        )


class Question(BaseModel):
    id: QuestionID
    text: str
    answers: List[Union[str, int]]

    def template(self) -> Dict[str, Union[str, Callable[[str], str]]]:
        return QUESTION_TEMPLATES[self.id.template_index]


class SelectedQuestion(BaseModel):
    question: Question
    asked: Set[QuestionID]


class Answer(BaseModel):
    question: Question
    given_answer: str


class CSRFException(Exception):
    def __init__(self, args):
        self.args = args
