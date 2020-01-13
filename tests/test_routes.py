#
import os
import random
from json import loads
from pathlib import Path

#
import boto3
import pytest
import toml
from moto import mock_dynamodb2
from pytest import fixture
from starlette.testclient import TestClient

#
from bgt import (QUESTION_TEMPLATES, Answer, Feedback, Game, Games, Question,
                 QuestionSelector, Score, UniversalEncoder, __version__,
                 extract_attr)


def test_root(games_data: Games, client):
    "Should return the current version and the number of possible questions"
    response = client.get("/")
    assert response.status_code == 200
    assert loads(response.content) == {
        "version": f"v{__version__}",
        "question_count": len(games_data.all_qids)
    }


def test_get_question(client):
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


def test_get_answer(client, games_data: Games,
question_selector: QuestionSelector):
    test_question: Question = question_selector.next_question().question
    a = Answer(
        question=test_question,
        given_answer=random.choice(test_question.answers)
    )
    response = client.post(
        "/answers/",
        data=a.json()
    )
    assert response.status_code == 200
    feedback = Feedback(games=games_data, **loads(response.content))
    assert feedback.given_answer in feedback.answer.question.answers
    assert feedback.is_correct or not feedback.is_correct


def test_put_scores(client,fake_score):
    headers = {
      "Origin": "http://localhost:8080",
      "x-requested-with": "test"
    }
    response = client.post(
      "/scores/", data=fake_score.json(), headers=headers)
    assert response.status_code == 200
    final_score = Score(**loads(response.content))
    assert final_score.dict() == fake_score.dict()
    assert final_score.score == 100

def test_get_scores(client):
    response = client.get(
        "/scores/"
    )
    raw_scores = loads(response.content)
    scores = [Score(**s) for s in raw_scores]
    assert len(scores) == 10
    for i, score in enumerate(scores[:-1]):
        assert score.score > scores[i+1].score

def test_get_5_scores(client):
    response = client.get(
        "/scores/?n=5"
    )
    raw_scores = loads(response.content)
    scores = [Score(**s) for s in raw_scores]
    assert len(scores) == 5
    for i, score in enumerate(scores[:-1]):
        assert score.score > scores[i+1].score
