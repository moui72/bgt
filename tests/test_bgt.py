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


@fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'


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
def setup_db(games_data, aws_credentials):
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


def test_version():
    assert __version__ == '0.1.0'


def test_root(setup_db):
    client = setup_db
    response = client.get("/")
    assert response.status_code == 200


def test_get_game(games_data, setup_db):
    client = setup_db
    test_game = games_data[randint(0, 24)]
    assert hasattr(test_game, "id")
    response = client.get(f"/games/{test_game.id}")
    assert response.status_code == 200


def test_get_games(setup_db):
    client = setup_db
    response = client.get(f"/games/")
    result = loads(response.content)
    assert response.status_code == 200
    assert len(result["Items"]) == 25


def test_get_nogame(outside_game_data, setup_db):
    client = setup_db
    test_game = outside_game_data
    assert hasattr(test_game, "id")
    assert outside_game_data.id == 59946
    response = client.get(f"/games/{test_game.id}")
    assert response.status_code == 404
