
import requests
import pytest
import boto3
import os
from random import randint
from moto import mock_dynamodb2
from json import load, dump
from starlette.testclient import TestClient
from app import __version__
from app.main import app
from app.schema import Game
from app.utils import take, UniversalEncoder

client = TestClient(app)


def rel_path(fn):
    return os.path.join(os.path.dirname(__file__), fn)


def local_url(path):
    return "http://localhost:8000"+path


def test_version():
    assert __version__ == '0.1.0'


def test_root():
    response = client.get("/")
    assert response.status_code == 200


@mock_dynamodb2
def test_get_game():
    # load table scheme
    scheme_fp = rel_path("gameTableScheme.json")
    with open(scheme_fp, "r") as scheme_json:
        scheme = load(scheme_json)

    # load game data
    games_put_fp = rel_path("games_to_put.json")
    with open(games_put_fp, "r") as games_put_json:
        games = load(games_put_json)

    # validate/cast game data
    Games = []
    for game in games:
        Games.append(Game(**game))

    # create dynamodb interface (mocked by moto decorator)
    dynamodb = boto3.resource('dynamodb', 'us-east-1')

    # create table with scheme
    table = dynamodb.create_table(
        **scheme
    )

    # put games in table
    with table.batch_writer() as batch:
        for game in Games:
            batch.put_item(game.dict())

    test_game = Games[randint(0, 24)]
    assert hasattr(test_game, "Id")
    response = client.get("/games/"+str(test_game.Id))
    assert response.status_code >= 200 and response.status_code <= 299

# resp = requests.get(local_url("/game/"))
# print(resp.json())
# assert_that(resp.ok, 'HTTP Request OK').is_true()
