# std
import os
from random import randint
from pathlib import Path
from json import load, dump, loads

# vendor
from moto import mock_dynamodb2
import pytest
from pytest import fixture
import boto3
from starlette.testclient import TestClient

# local
from app._version import __version__
from app.schema import Game
from app.utils import UniversalEncoder

@fixture(autouse=True)
def _aws_credentials(monkeypatch):
    """Mocked AWS Credentials for moto."""
    monkeypatch.setitem(os.environ, "AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setitem(os.environ, "AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setitem(os.environ, "AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setitem(os.environ, "AWS_SESSION_TOKEN", "testing")
    yield



@fixture
def create_table():
    # create dynamodb interface (mocked by moto decorator)
    dynamodb = boto3.resource('dynamodb', 'us-east-1')
    table_name = "GamesTest"

    table = dynamodb.Table(table_name)
    try:
        if table.item_count >= 0:
            print("table exists, deleting")
            table.delete()
            table.meta.client.get_waiter(
                'table_not_exists').wait(TableName=table_name)
    except Exception as e:
        if "ResourceNotFoundException" not in str(e):
            raise e

    # load schema from file
    with open(Path(__file__).parent.parent / "games_table_schema.json", "r") as schema_json:
        schema = load(schema_json)

    # create table with schema
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

    with open('games.json', 'r') as jsongames:
        games = load(jsongames)

    valid_games = [Game(**game) for game in games.values()]

    if (table.item_count > 0):
        print("skipping insertion")
    else:
        with table.batch_writer() as batch:
            for game in valid_games:
                batch.put_item(game.dict())

    shuffle(valid_games)
    with open(Path(__file__).parent/"tests/games_test_data.json", 'w') as test_set:
        dump(valid_games[:25], test_set, cls=UniversalEncoder, indent=2)
    with open(Path(__file__).parent/"tests/outside_game.json", 'w') as outside_game:
        dump(valid_games[-1], outside_game, cls=UniversalEncoder, indent=2)
    yield table




@fixture
def games_data():
    # load game data
    with open(Path(__file__).parent/"games_test_data.json", "r") as games_put_json:
        games_raw = load(games_put_json)
        # validate/cast game data
    games = []
    for game in games_raw:
        games.append(Game(**game))
    return games


@fixture
def outside_game_data():
    with open(Path(__file__).parent/"outside_game.json", "r") as outside_game_json:
        return Game(**load(outside_game_json))


@fixture
def client(games_data):
    with mock_dynamodb2():
        # load table schema
        with open(Path(__file__).parent.parent/"games_table_schema.json", "r") as schema_json:
            schema = load(schema_json)

        # create dynamodb interface (mocked by moto decorator)
        dynamodb = boto3.resource('dynamodb', 'us-east-1')

        # create table with schema
        table = dynamodb.create_table(
            **schema
        )
        table.wait_until_exists()

        # put games in table
        with table.batch_writer() as batch:
            for game in games_data:
                batch.put_item(game.dict())
        from app._main import app
        client = TestClient(app)
        yield client
