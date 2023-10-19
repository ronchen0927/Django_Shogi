import pickle
import base64

from django.shortcuts import render, redirect
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
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


class RuleAPIView(APIView):
    DESCRIPTION = '''棋盤和棋子：將棋的棋盤由9x9的格子組成。兩位玩家各有20個棋子，包括王、飛車、角行、金將、銀將、桂馬、香車、歩兵。
遊戲的目標：對手的王將被將軍無法逃脫時獲勝。
移動棋子：每個棋子都有其特定的移動方式。當棋子進入敵人的三行之內時，有些棋子可以升級，獲得新的移動能力。
取得對方棋子：當你的棋子移動到對方的棋子所在的位置，你可以取得該棋子。你可以選擇在接下來的任何回合使用取得的棋子，並將其放回棋盤上繼續遊戲。但是，它必須是你的方向且未升級的狀態。
升級棋子：當棋子進入敵方的陣地（最後三排）時，大多數棋子都可以升級。升級後的棋子會翻面，顯示其升級的身分，並獲得新的移動能力。
規則限制：不能使自己的王被將軍。不能連續移動兩次使對方處於將軍狀態，除非每一步都更加接近將軍狀態。步兵、飛車和角行不能連續且不間斷地移動到同一列。
特殊情況：若遊戲進入重複的位置和移動模式，該遊戲可能被判為平局。
結束遊戲：當一方的王被將軍且無法逃脫，對方獲勝。如果一方認為無法獲勝，他可以選擇投降。
'''

    def get(self, request):
        rules = {
            'title': '將棋規則',
            'description': self.DESCRIPTION
        }
        return Response(rules)