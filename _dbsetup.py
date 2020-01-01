from json import load, dump
from typing import Dict, List, Set
from decimal import Decimal
from enum import Enum
from types import GeneratorType
from pathlib import Path
from random import shuffle
import datetime

import boto3
from boardgamegeek import BGGClient, CacheBackendSqlite

from app.schema import Game
from app.utils import oxford_join, UniversalEncoder

delete_existing = input("Delete existing table? y/N\n") or "N"
if (delete_existing[0] in ["y", "Y"]):
    delete_existing = True
else:
    delete_existing = False


def create_table():
    # create dynamodb interface (mocked by moto decorator)
    dynamodb = boto3.resource('dynamodb', 'us-east-1')
    table_name = "GamesTest"

    table = dynamodb.Table(table_name)
    if (delete_existing):
        try:
            if table.item_count >= 0:
                print("table exists, deleting")
                table.delete()
                table.meta.client.get_waiter(
                    'table_not_exists').wait(TableName=table_name)
        except Exception as e:
            if "ResourceNotFoundException" not in str(e):
                raise e
            else:
                print("table not exists")

    # load schema from file
    with open(Path(__file__).parent.parent / "games_table_schema.json", "r") as schema_json:
        schema = load(schema_json)

    # create table with scheme
    print("creating table")
    try:
        if (table.item_count == 0):
            table = dynamodb.create_table(
                **schema
            )
            table.meta.client.get_waiter(
                'table_exists').wait(TableName=table_name)
    except Exception as e:
        if "ResourceInUseException" in str(e):
            print("table already exists")
        else:
            raise e
    return table


def put_data(table):
    print(f"table contains {table.item_count} items")
    with open('games.json', 'r') as jsongames:
        games = load(jsongames)

    valid_games = [Game(**game) for game in games.values()]
    print(f"putting {len(valid_games)} items in table")
    if (table.item_count > 0):
        print("skipping insertion")
    else:
        with table.batch_writer() as batch:
            for game in valid_games:
                batch.put_item(game.dict())
    print("generating test data")
    shuffle(valid_games)
    with open(Path(__file__).parent/"tests/games_test_data.json", 'w') as test_set:
        dump(valid_games[:25], test_set, cls=UniversalEncoder, indent=2)
    with open(Path(__file__).parent/"tests/outside_game.json", 'w') as outside_game:
        dump(valid_games[-1], outside_game, cls=UniversalEncoder, indent=2)
    return table


table = put_data(create_table())

print(f"Table contains {table.item_count} items")
