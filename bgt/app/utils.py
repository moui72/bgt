
# std
import datetime
import json
from itertools import islice
from typing import Dict, List, Set
from decimal import Decimal
from enum import Enum
from types import GeneratorType

# vendor

# local 
from .schema import Game

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
    }

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        try:
            encoder = self.ENCODER_BY_TYPE[type(obj)]
        except KeyError:
            return super().default(obj)
        return encoder(obj)


def oxford_join(items: List):
    "joins a list with a comma, but uses 'and' before the last item"
    if len(items) < 1:
        raise ValueError("Can't join an empty list")
    if len(items) == 1:
        return items[0]
    oxford_comma = (",","")[len(items) == 2]
    return ', '.join(items[:-1]) + f'{oxford_comma} and {items[-1]}'

