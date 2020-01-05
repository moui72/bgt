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
def client(games_data):
    with mock_dynamodb2(): 
        # create dynamodb interface (mocked by moto decorator)
        dynamodb = boto3.resource('dynamodb', 'us-east-1')
        table_name = "GamesTest"
        table = dynamodb.Table(table_name)
        # load schema from file
        with open(
            Path(__file__).parent.parent / "games_table_schema.json", "r"
        ) as schema_json:
            schema = load(schema_json)
        # create table with schema
        try:
            table = dynamodb.create_table(
                **schema
            )
            table.meta.client.get_waiter(
                'table_exists'
            ).wait(TableName=table_name)
        except Exception as e:
            if "ResourceInUseException" not in str(e):
                raise e
        with table.batch_writer() as batch:
            for game in games_data:
                batch.put_item(game.dict())
        from app._main import create_app
        app = create_app()
        client = TestClient(app)
        yield client


@fixture
def games_data():
    # load game data
    with open(Path(__file__).parent.parent/"games.json", "r") as games_put_json:
        games_raw = load(games_put_json)
        # validate/cast game data
    games = []
    for game in games_raw.values():
        games.append(Game(**game))
    return games
