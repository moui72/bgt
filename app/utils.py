
# stdlib
import datetime
import json
from itertools import islice
from typing import Dict, List, Set
from decimal import Decimal
from enum import Enum
from types import GeneratorType

# third party
from boardgamegeek import BGGClient, CacheBackendSqlite

# local
from app.schema import Game


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))


def update_schema(game):
    "takes a game with old scheme (lowercase props) and renames (uppercase)" "renames year_published to Year"
    return {
        "Name": game['name'],
        "Id": game['id'],
        "Fetched": game['fetched'],
        "Developers": game['developers'],
        "Year": game['year_published']
    }


class UniversalEncoder(json.JSONEncoder):
    # I got this from stack overflow, should find again and credit the author
    ENCODER_BY_TYPE = {
        datetime.datetime: lambda dt: dt.isoformat(),
        datetime.date: lambda dt: dt.isoformat(),
        datetime.time: lambda dt: dt.isoformat(),
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
    "joins a list with a comma, but used 'and' before the last item"
    if (len(items) < 1):
        return None
    if len(items) == 1:
        return items[0]
    result = ', '.join(items[:-1]) + ' and ' + items[-1]
    return result
