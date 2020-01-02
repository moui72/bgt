# std
import os
import toml
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
from app.schema import Game, Question
from app.utils import UniversalEncoder


def test_version():
    with open(Path(__file__).parent.parent / "pyproject.toml") as f:
        pyproject_toml = toml.load(f)
    assert __version__ == pyproject_toml["tool"]["poetry"]["version"]


def test_get_nogame(outside_game_data, client):
    "Makes sure we're testing against the mocked DB and not the real one"
    test_game = outside_game_data
    assert hasattr(test_game, "id")
    assert outside_game_data.id == 59946
    response = client.get(f"/games/{test_game.id}")
    assert response.status_code == 404


def test_root(client):
    "Should return the current version"
    response = client.get("/")
    assert response.status_code == 200


def test_get_game(games_data, client):
    "Should successfully get game by id"
    test_game = games_data[randint(0, 24)]
    response = client.get(f"/games/{test_game.id}")
    assert hasattr(test_game, "id")
    assert response.status_code == 200


def test_get_games(client):
    "Should successfully get all games"
    response = client.get(f"/games/")
    result = loads(response.content)
    assert response.status_code == 200
    assert len(result) == 25

def test_get_question(games_data, client):
    "GET questions takes 1 query param, asked --"
    "asked is a comma separated list of question ids that have been asked"
    "memo is passed back and forth between server and client to ensure "
    "questions are not repeated"
    ids = set(g.id for g in games_data)
    asked = []
    for i in range(10):
        query_string = f"?asked={','.join(asked)}" if len(asked) > 0 else ''
        response = client.get(
            "/questions/" + query_string 
        )
        assert response.status_code == 200
        response_body = loads(response.content)
        asked = [] if response_body["asked"] is None else response_body["asked"].split(",") 
        question = Question(**response_body["question"])
        assert question.id not in asked
        q, g = (int(s) for s in question.id.split("-"))
        assert q >= 0 and q <= 3
        assert g in ids
        asked.append(question.id)