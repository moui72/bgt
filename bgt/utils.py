
from typing import Dict, List, Set
from decimal import Decimal
from enum import Enum
from types import GeneratorType
from boardgamegeek import BGGClient, CacheBackendSqlite
from schema import Game
import datetime
import json


def isoformat(o):
    return o.isoformat()


class UniversalEncoder(json.JSONEncoder):
    ENCODER_BY_TYPE = {
        datetime.datetime: isoformat,
        datetime.date: isoformat,
        datetime.time: isoformat,
        set: list,
        frozenset: list,
        GeneratorType: list,
        bytes: lambda o: o.decode(),
        Decimal: str,
        Game: dict,
    }

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        try:
            encoder = self.ENCODER_BY_TYPE[type(obj)]
        except KeyError:
            return super().default(obj)
        return encoder(obj)


def oxford_join(items):
    if (len(items) < 1):
        return None
    if len(items) == 1:
        return items[0]
    result = ', '.join(items[:-1]) + ' and ' + items[-1]
    return result
