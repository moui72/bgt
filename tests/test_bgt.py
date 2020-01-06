# std
import os
import toml
import random
from pathlib import Path
from json import loads

# vendor
from moto import mock_dynamodb2
import pytest
from pytest import fixture
import boto3
from starlette.testclient import TestClient

# local
from bgt import (
    __version__,
    Game, 
    Question, 
    question_templates,
    UniversalEncoder,
    Question_Selector, 
    Games
)

def test_version():
    with open(Path(__file__).parent.parent / "pyproject.toml") as f:
        pyproject_toml = toml.load(f)
    assert __version__ == pyproject_toml["tool"]["poetry"]["version"]


def test_root(client, games_data):
    "Should return the current version and the number of possible questions"
    response = client.get("/")
    assert response.status_code == 200
    assert loads(response.content) == {
        "version": f"v{__version__}", 
        "question_count": len(games_data) * len(question_templates)
    }


def test_get_question(games_data, client):
    ids = set(g.id for g in games_data)
    asked = []
    for i in range(3):       
        if len(asked) > 0:
            query_string = f"?asked={','.join(str(a) for a in asked)}"
        else:
            query_string = ''
        response = client.get(
            "/questions/" + query_string 
        )
        assert response.status_code == 200
        response_body = loads(response.content)
        question = Question(**response_body["question"])
        # make sure no question is served twice 
        assert question.id not in asked
        if response_body["asked"] is not None:
            asked = response_body["asked"]


def test_question_selector(games_data):
    qs = Question_Selector(games=Games(games_data),asked=[])
    q1 = qs.nextQuestion({str(q) for q in qs.asked}) 
    q2 = qs.nextQuestion({str(q) for q in qs.asked}) 
    assert q1 != q2
    assert len(q1["asked"]) < len(q2["asked"])
    assert q1["asked"].issubset(q2["asked"])
    assert len(q1["question"].answers) == 4