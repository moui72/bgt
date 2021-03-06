# Standard lib
import os
from json import dump, load, loads
from pathlib import Path
from random import randint, shuffle
from typing import List

# Vendor
import boto3
import pytest
from moto import mock_dynamodb2
from pytest import fixture
from starlette.testclient import TestClient

# Absolute local
from bgt import (QUESTION_TEMPLATES, DatabaseConnection, Game, Games, Question,
                 QuestionID, QuestionSelector, Score, UniversalEncoder,
                 create_app)


@fixture(autouse=True)
def _aws_credentials(monkeypatch):
    """Mocked AWS Credentials for moto."""
    monkeypatch.setitem(os.environ, "AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setitem(os.environ, "AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setitem(os.environ, "AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setitem(os.environ, "AWS_SESSION_TOKEN", "testing")
    yield


@fixture
def client(games_data, fake_scores):
    with mock_dynamodb2():
        db = DatabaseConnection()
        dynamodb = db.connection
        table_name = "GamesTest"
        table = dynamodb.Table(table_name)
        with open(
            Path(__file__).parent.parent / "games_table_schema.json", "r"
        ) as schema_json:
            schema = load(schema_json)
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
            for game in games_data.all_games:
                batch.put_item(game.dict())
        table_name = "ScoresTest"
        table = dynamodb.Table(table_name)
        with open(
                Path(__file__).parent.parent / "scores_table_schema.json", "r"
            ) as schema_json:
                schema = load(schema_json)
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
            for score in fake_scores:
                batch.put_item(score.dict())
        app = create_app(db=db)
        yield TestClient(app)


@fixture
def games_data() -> Games:
    # load game data
    with open(Path(__file__).parent.parent/"games.json", "r") as games_put_json:
        games_raw = load(games_put_json)
    return Games(all_games=[Game(**game) for game in games_raw.values()])


@fixture
def question_selector(games_data: Games) -> QuestionSelector:
    return QuestionSelector(games=games_data, asked=[])


@fixture
def sample_game(games_data: Games) -> Game:
    return games_data.all_games_by_id[155122]


@fixture
def sample_question_game_by_dev(
    sample_game: Game,
    question_selector: QuestionSelector
) -> Question:
    return question_selector.make_question(
        QuestionID(template_index=0, right_game=sample_game.id)
    )


@fixture
def sample_question_game_in_year(
    sample_game: Game,
    question_selector: QuestionSelector
) -> Question:
    return question_selector.make_question(
        QuestionID(template_index=1, right_game=sample_game.id)
    )


@fixture
def sample_question_dev_of_game(
    sample_game: Game,
    question_selector: QuestionSelector
) -> Question:
    return question_selector.make_question(
        QuestionID(template_index=2, right_game=sample_game.id)
    )


@fixture
def sample_question_year_of_game(
    sample_game: Game,
    question_selector: QuestionSelector
) -> Question:
    return question_selector.make_question(
        QuestionID(template_index=3, right_game=sample_game.id)
    )



@fixture
def fake_score(): 
    return Score(name="TJP", score=100)

@fixture
def fake_scores(fake_score: Score) -> List[Score]:
    scores = []
    for n in range(20):
        score = fake_score.copy(update={"score": fake_score.score - n})
        scores.append(score)
    shuffle(scores)
    return scores