
import os
import random
from json import loads
from pathlib import Path

import boto3
import pytest
import toml
from moto import mock_dynamodb2
from pytest import fixture
from starlette.testclient import TestClient

from bgt import (QUESTION_TEMPLATES, Answer, Feedback, Game, Games, Question,
                 QuestionSelector, Score, UniversalEncoder, __version__,
                 extract_attr)


def test_version():
    with open(Path(__file__).parent.parent / "pyproject.toml") as f:
        pyproject_toml = toml.load(f)
    assert __version__ == pyproject_toml["tool"]["poetry"]["version"]


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
    assert sample_question_year_of_game.text
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


def test_feedback_question_game_by_dev(
    sample_game, sample_question_game_by_dev, games_data
):
    correct_answer = extract_attr(
        game=sample_game,
        attr=sample_question_game_by_dev.template()["answer_type"]
    )
    fake_response = Answer(
        question=sample_question_game_by_dev,
        given_answer=correct_answer
    )
    correct_feedback = Feedback(
        games=games_data,
        answer=fake_response
    )
    assert correct_feedback.is_correct
    assert correct_feedback.response_text == f"Yes, {correct_answer} is right"
    other_answers = sample_question_game_by_dev.answers
    other_answers.remove(correct_answer)
    incorrect_answer = random.choice(tuple(other_answers))
    fake_response = Answer(
        question=sample_question_game_by_dev,
        given_answer=incorrect_answer
    )
    incorrect_feedback = Feedback(games=games_data, answer=fake_response)
    assert not incorrect_feedback.is_correct
    assert incorrect_feedback.response_text == f"Sorry, the answer was {correct_answer}, not {incorrect_answer}"


def test_feedback_question_game_in_year(
    sample_game, sample_question_game_in_year, games_data
):
    correct_answer = extract_attr(
        game=sample_game,
        attr=sample_question_game_in_year.template()["answer_type"]
    )
    fake_response = Answer(
        question=sample_question_game_in_year,
        given_answer=correct_answer
    )
    correct_feedback = Feedback(
        games=games_data,
        answer=fake_response
    )
    assert correct_feedback.is_correct
    assert correct_feedback.response_text == f"Yes, {correct_answer} is right"
    other_answers = sample_question_game_in_year.answers
    other_answers.remove(correct_answer)
    incorrect_answer = random.choice(tuple(other_answers))
    fake_response = Answer(
        question=sample_question_game_in_year,
        given_answer=incorrect_answer
    )
    incorrect_feedback = Feedback(games=games_data, answer=fake_response)
    assert not incorrect_feedback.is_correct
    assert incorrect_feedback.response_text == f"Sorry, the answer was {correct_answer}, not {incorrect_answer}"


def test_feedback_question_dev_of_game(
    sample_game, sample_question_dev_of_game, games_data
):
    correct_answer = extract_attr(
        game=sample_game,
        attr=sample_question_dev_of_game.template()["answer_type"]
    )
    fake_response = Answer(
        question=sample_question_dev_of_game,
        given_answer=correct_answer
    )
    correct_feedback = Feedback(
        games=games_data,
        answer=fake_response
    )
    assert correct_feedback.is_correct
    assert correct_feedback.response_text == f"Yes, {correct_answer} is right"
    other_answers = sample_question_dev_of_game.answers
    other_answers.remove(correct_answer)
    incorrect_answer = random.choice(tuple(other_answers))
    fake_response = Answer(
        question=sample_question_dev_of_game,
        given_answer=incorrect_answer
    )
    incorrect_feedback = Feedback(games=games_data, answer=fake_response)
    assert not incorrect_feedback.is_correct
    assert incorrect_feedback.response_text == (f"Sorry, the answer was "
    f"{correct_answer}, not {incorrect_answer}")

def test_score(fake_score):
    pass