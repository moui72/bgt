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
    extract_attr,
    question_templates,
    Answer,
    Feedback,
    Game,
    Games,
    Question,
    QuestionSelector,
    UniversalEncoder,
)


def test_version():
    with open(Path(__file__).parent.parent / "pyproject.toml") as f:
        pyproject_toml = toml.load(f)
    assert __version__ == pyproject_toml["tool"]["poetry"]["version"]


def test_root(games_data: Games, client):
    "Should return the current version and the number of possible questions"
    response = client.get("/")
    assert response.status_code == 200
    assert loads(response.content) == {
        "version": f"v{__version__}",
        "question_count": len(games_data.all_qids)
    }


def test_get_question(games_data: Games, client):
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


def test_get_answer(games_data: Games, client, question_selector):
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


def test_question_selector(games_data, question_selector):
    q1 = question_selector.next_question()
    q2 = question_selector.next_question()
    assert q1.question != q2.question
    assert q1.asked.issubset(q2.asked)
    assert len(q1.question.answers) == 4
    question_selector = QuestionSelector(
        games=games_data,
        asked=question_selector.asked
    )
    q3 = question_selector.next_question()
    assert q3.question != q2.question
    assert q2.asked.issubset(q3.asked)


def test_feedback_question_year_of_game(
    sample_game, sample_question_year_of_game, games_data
):

    correct_answer = extract_attr(
        game=sample_game,
        attr=sample_question_year_of_game.template()["answer_type"]
    )
    fake_response = Answer(
        question=sample_question_year_of_game,
        given_answer=correct_answer
    )
    correct_feedback = Feedback(
        games=games_data,
        answer=fake_response
    )
    assert correct_feedback.is_correct
    assert correct_feedback.response_text == f"Yes, {correct_answer} is right"
    other_answers = sample_question_year_of_game.answers
    other_answers.remove(correct_answer)
    incorrect_answer = random.choice(tuple(other_answers))
    fake_response = Answer(
        question=sample_question_year_of_game,
        given_answer=incorrect_answer
    )
    incorrect_feedback = Feedback(games=games_data, answer=fake_response)
    assert not incorrect_feedback.is_correct
    assert incorrect_feedback.response_text == f"Sorry, the answer was {correct_answer}, not {incorrect_answer}"
