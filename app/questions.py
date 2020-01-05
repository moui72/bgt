# std imports
import random
from typing import List, Set, Tuple, Dict
from datetime import datetime

# vendor imports
from pydantic import BaseModel, conint, PositiveInt
import boto3

# local imports
from app.schema import (
    Game, question_templates, Score, QID, Question, qid_from_str
)
from app.utils import oxford_join

class Games:
    all_games: List[Game]
    all_game_ids: Tuple[PositiveInt]
    all_games_by_id: Dict[int,Game]
    all_qids: Set[QID]

    def __init__(self, games = None):
        self.all_games = games or self.query_games()
        self.all_game_ids = tuple(g.id for g in self.all_games)
        self.all_games_by_id = {g.id: g for g in self.all_games}
        self.all_qids = set(
            QID(template_index=template_index, right_game=game) 
            for template_index in range(len(question_templates)) 
            for game in self.all_game_ids
        )


    def query_games(self):
        dynamodb = boto3.resource('dynamodb', 'us-east-1')
        table = dynamodb.Table('GamesTest')
        raw_games = table.scan()
        return [Game(**g) for g in raw_games["Items"]]

class QuestionSelector:
    asked: Set[str] = set()
    _games: Games
    _free_qids: Set[QID] = None

    def __init__(self,asked,games):
        self.asked = set(qid_from_str(a) for a in asked)
        self._games = games
        self.update_free_qids()

    def nextQuestion(self,asked = None):
        self.update_free_qids(asked)
        new_qid = random.choice(tuple(self._free_qids))
        right_game = self._games.all_games_by_id[new_qid.right_game]
        template = question_templates[new_qid.template_index]
        text_fill = getattr(right_game, template["answer_type"])
        self.asked.add(new_qid)
        answers = self.get_answers(new_qid)
        return {
            "question": Question(
                id=new_qid,
                text=template["text"](text_fill),
                answers=answers
            ), 
            "asked": self.asked.copy()
        }
    
    def update_free_qids(self, asked = None):
        if asked is not None:
            asked = [qid_from_str(a) for a in asked]
        else:
            asked = self.asked
        if self._free_qids is None:
            self._free_qids = set(
                qid for qid in self._games.all_qids 
                if qid not in asked
            )

        if asked is not None and self.asked.issubset(asked):
            for qid in asked:
                self._free_qids.remove(qid)

    def get_answers(self, qid: QID):
        template = qid.template()
        game = self._games.all_games_by_id[qid.right_game]
        right_answer = getattr(game, template["answer_type"])
        answers = set()
        if template["answer_type"] == "developers":
            right_answer = oxford_join(right_answer) 
        answers.add(right_answer)
        while len(answers) < 4:
            if template["answer_type"] == "year":
                alt_answer = random.randint(
                    game.year-10,
                    min(datetime.now().year, game.year+10)
                )
            else:
                alt_answer = getattr(
                    random.choice(self._games.all_games), 
                    template["answer_type"]
                )
            if template["answer_type"] == "developers":
                alt_answer = oxford_join(alt_answer)
            answers.add(alt_answer)
        answers = list(answers)
        random.shuffle(answers)
        return answers
