# Design plan

## Summary

Users get a question like, "Who designed 'Carcassone'?" and must choose from a closed set of answers, e.g.:

1. Klaus Teuber
2. Klaus-Jürgen Wrede
3. Bruno Cathala
4. R. Eric Reuss

Users have 10sec and get a point for every right answer. After two wrong answers, the game is over. An arcade-game style leader board will track top scores.

## Data preparation

The following types of questions will be available to start:

* "QUESTION": Who designed (GAME)?
  * "ANSWER": [(DESIGNER)]
* "QUESTION": Which game was designed by (DESIGNER)?
  * "ANSWER": [(GAME)]
* "QUESTION": When was (GAME) released?
  * "ANSWER": [(YEAR)]
* "QUESTION": Which game came out in (YEAR)?
  * "ANSWER": [(GAME)]

To start, a database of ~700 games, their years published, and their designers, will be built. Database will be in AWS Dynamo DB.

## Interfaces

### Backend

FastAPI. Endpoints "for":

#### GAME

GET Respond with complete game

`{ "id": INT, "name": STRING, "yearPublished": INT, "designers": STRING}`

#### DESIGNER

GET Respond with complete designer

`{ "id": INT, "name": STRING}`

#### QUESTION

GET   (requires logic)

Pick a random question template (in source, e.g.,  \
`{"q": "Who designed __GAME__?” "a": “__GAME__.DESIGNER"}`)

Pick a random "correct" game and fill in slots

Get alternatives (for game or designer, pick random; for year, do math)

Check for false negatives among alternative answers, replace until clean

Respond with complete question

`{ "id": INT, "template": STRING, "answers": [STRING], "correct_answer": INT}`

#### SCORE

POST  Add a score

GET  Get a score

`{ "id": INT, "playerName": STRING, "score": INT }`

### Frontend

ReactJS SPA. No routing, initially. MobX for state management?

#### Components

"Pages": Play game, Leaderboard, Help/info/about

##### Play game

###### Start game

default display, button to begin a new game

###### Current score

number of correct answers so far

###### Lives remaining

Display (2 - number of incorrect answers so far).  End game when 0.

###### Question

Display the question text

###### Answers

Provide buttons for each answer option; handle correct/incorrect responses

###### Result

After response, before next question/game end, tell player if they got it right or wrong. On dismiss, go to next question or
game over

###### Timer

Display (10 - seconds elapsed on this question). Trigger incorrect response when 0

###### Game over

Inform the player the game has ended. Navigate to leaderboard on dismiss.

###### Add score form

If score is in the top ten, get player name to add to leaderboard.

##### Leaderboard components

###### Scores

Container for row of 10 top scores, sorted DESC

###### Score

Display "PLAYER NAME -- SCORE"

#### CLient State

Front end state

```jsonc
{
  "view": "leaderboard” | “game", // which page we’re on
  "question" {}, // the current question -- empty when game has not started
  "asked": [], // list of last (max 100) question ids -- empty when game has not started
  "nextQuestions": [], // upcoming questions -- empty when game has not started
  "score": 0, // number of correct answers so far
  "wrongAnswers": 0, // number of wrong answers so far; 2 = game over
  "playerName": "", // for leadboard; prompt after each highscore game (but remember last)
  "scores": [
    { "playerName": "", "score": 0 }, // for leaderboard, top 10 scores
  ]

}
```