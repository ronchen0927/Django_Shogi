# Shogi
## Introduction
[Game rules](https://zh.wikipedia.org/zh-tw/%E6%97%A5%E6%9C%AC%E5%B0%86%E6%A3%8B)
---

Init board
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
```
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

#### Runserver
```bash
python manage.py runserver
```
## How to Play
<strong>Temporarily using both swagger and postman to make API calls for playing chess</strong>
http://127.0.0.1:8000/swagger/

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
Drop "Pawn" to d4
```
P*d4
```
Drop "Rook" to g5
```
R*g5
```