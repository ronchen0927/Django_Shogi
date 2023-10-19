import pickle
import base64

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .game import ShogiGame
from .models import Player
from .models import Game
from .models import Move


def reset_session(request):
    request.session.clear()
    return redirect('../game/')


def game_board(request):
    encoded_game = request.session.get('game')

    if encoded_game:
        game_bytes = base64.b64decode(encoded_game)
        game = pickle.loads(game_bytes)
    else:
        game = ShogiGame()
        

    if request.method == 'POST':
        move = request.POST.get('move')

        try:
            game.current_player = game.players[game.game_round % 2]

            game.board.execute_move(move, game.current_player)
            result = game.get_game_ended(game.players[0], game.players[1])

            if result:
                # Game over
                winner = result

                if winner == 1:
                    print(f"Winner is {game.players[0].name}")
                else:
                    print(f"Winner is {game.players[1].name}")

            game.game_round += 1

            # Use "pickle" to serialization shogi game object
            # then transfer to base64
            # Finally store to session
            game_bytes = pickle.dumps(game)
            request.session['game'] = base64.b64encode(game_bytes).decode('utf-8')
        except Exception as e:
            pass

    return render(request, 'game_board.html', {'board': game.board})