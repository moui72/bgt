
# Standard lib
import datetime
import json
from decimal import Decimal
from enum import Enum
from itertools import islice
from types import GeneratorType
from typing import Dict, List, Set, Union

# Relative local
from .datatypes import Game, Question, QuestionID, SelectedQuestion


class UniversalEncoder(json.JSONEncoder):
    # I got this from stack overflow, should find again and credit the author
    ENCODER_BY_TYPE = {
        datetime.datetime: datetime.datetime.isoformat,
        datetime.date: datetime.date.isoformat,
        datetime.time: datetime.time.isoformat,
        set: list,
        frozenset: list,
        GeneratorType: list,
        bytes: bytes.decode,
        Decimal: str,
        Game: Game.json,
        SelectedQuestion: SelectedQuestion.json,
        Question: Question.json,
        QuestionID: str,
    }

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        if hasattr(obj, "json"):
            try:
                return obj.json()
            except TypeError as e:
                if "not callable" in e:
                    return obj.json
        try:
            encoder = self.ENCODER_BY_TYPE[type(obj)]
        except KeyError:
            return super().default(obj)
        return encoder(obj)


def oxford_join(items: List[Union[str, int]]) -> str:
    "joins a list with a comma, but uses 'and' before the last item"
    if len(items) < 1:
        return ""
    if len(items) == 1:
        return str(items[0])
    oxford_comma = (",", "")[len(items) == 2]
    return ', '.join(items[:-1]) + f'{oxford_comma} and {items[-1]}'


def extract_attr(game: Game, attr: str) -> str:
    a = getattr(game, attr)
    if attr == "developers":
        return oxford_join(a)
    return str(a)