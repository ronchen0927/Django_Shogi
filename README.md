# Django Shogi
## Introduction
[Game rules](https://zh.wikipedia.org/zh-tw/%E6%97%A5%E6%9C%AC%E5%B0%86%E6%A3%8B)

---
Initial board
```
9 | L| N| S| G| K| G| S| N| L|
8 |__| R|__|__|__|__|__| B|__|
7 | P| P| P| P| P| P| P| P| P|
6 |__|__|__|__|__|__|__|__|__|
5 |__|__|__|__|__|__|__|__|__|
4 |__|__|__|__|__|__|__|__|__|
3 | p| p| p| p| p| p| p| p| p|
2 |__| b|__|__|__|__|__| r|__|
1 | l| n| s| g| k| g| s| n| l|
    a  b  c  d  e  f  g  h  i

Our Captures:
Opponent Captures:

我方玩家: foo
敵方玩家: bar
```
---
## Usage
#### Install requirement
```bash
pip install -r requirements.txt
```

#### Make migrations to the model
```bash
python manage.py makemigrations
python manage.py migrate
```

#### WebScoket: Open redis for Django channel layer
```bash
docker run --rm -p 6379:6379 redis:7
```

#### Runserver
```bash
python manage.py runserver
```
---
## API doc
http://127.0.0.1:8000/swagger/

---
## How to Play
You need two players to start the game

One player <strong>creates a game(建立新遊戲)</strong> and another player <strong>joins the game(加入遊戲)</strong>
And you can <strong>continue playing game(繼續遊戲)</strong> until it is finished

### Move
Move piece a3 to a4
```
a3a4
```
### Promotion move
Move piece h6 to h7 and promote
```
h6h7+
```
### Drop
Our player drop "Pawn" to d4
```
P*d4
```
Opponent player drop "Rook" to g5
```
r*g5
```