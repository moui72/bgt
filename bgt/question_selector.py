# std imports
import random
from typing import List, Set, Tuple, Dict
from datetime import datetime

# vendor imports
from pydantic import BaseModel, conint, PositiveInt, validator

# local imports
from .schema import (
    qid_from_str, question_templates, Answer, Game, Games, Score,
    SelectedQuestion,  QuestionID, Question,
)
from .utils import oxford_join


class QuestionSelector:
    asked: Set[QuestionID] = set()
    _games: Games
    _free_qids: Set[QuestionID] = None

    def __init__(self, asked, games):
        self._games = games
        self.asked = set(asked)
        self._free_qids = set(
            qid for qid in self._games.all_qids
            if qid not in self.asked
        )

    def make_question(self, qid: QuestionID):
        template = question_templates[qid.template_index]
        game = self._games.all_games_by_id[qid.right_game]
        text_fill = extract_attr(game=game, attr=template["question_type"])
        answers = self._get_answers(qid)
        return Question(
            id=qid,
            text=template["text"](text_fill),
            answers=answers
        )

    def next_question(self):
        new_qid = random.choice(tuple(self._free_qids))
        return SelectedQuestion(
            question=self.make_question(qid=new_qid),
            asked=self.asked.copy()
        )

    def _get_answers(self, qid: QuestionID) -> Set[str]:
        answers: Set[str] = set()
        template = qid.template()
        game = self._games.all_games_by_id[qid.right_game]
        right_answer = extract_attr(
            game=game, attr=template["answer_type"])
        answers.add(right_answer)
        while len(answers) < 4:
            if template["answer_type"] == "year":
                alt_answer = str(random.randint(
                    game.year-10,
                    min(datetime.now().year, game.year+10)
                ))
            else:
                alt_answer = extract_attr(
                    game=random.choice(self._games.all_games),
                    attr=template["answer_type"]
                )
            answers.add(alt_answer)
        answers = list(answers)
        random.shuffle(answers)
        return answers


class Feedback(BaseModel):
    answer: Answer
    games: Games
    correct_game: Game = None
    answer_type: str = None
    given_answer: str = None
    correct_answer: str = None
    is_correct: bool = None
    response_text: str = None

    @validator("correct_game", always=True)
    def derive_correct_game(cls, v, values):
        return values["games"].all_games_by_id[
            values["answer"].question.id.right_game
        ]

    @validator("answer_type", always=True)
    def derive_answer_type(cls, v, values):
        return values["answer"].question.template()["answer_type"]

    @validator("given_answer", always=True)
    def derive_given_answer(cls, v, values):
        return values["answer"].given_answer

    @validator("correct_answer", always=True)
    def derive_correct_answer(cls, v, values):
        print(values.keys)
        return extract_attr(values["correct_game"], values["answer_type"])

    @validator("is_correct", always=True)
    def derive_is_correct(cls, v, values):
        return values["given_answer"] == values["correct_answer"]

    @validator("response_text", always=True)
    def derive_response_text(cls, v, values):
        given = values["given_answer"]
        correct = values["correct_answer"]
        if values["is_correct"]:
            return f"Yes, {given} is right"
        else:
            return f"Sorry, the answer was {correct}, not {given}"

    def response(self):
        exclude = {k for k in self.__fields_set__ if "_" == k[0]}
        return self.dict(exclude={*exclude, "games"})


def extract_attr(game: Game, attr: str) -> str:
    a = getattr(game, attr)
    if attr == "developers":
        return oxford_join(a)
    return str(a)
