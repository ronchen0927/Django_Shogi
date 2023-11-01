import pickle
import base64

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import views, status, permissions, exceptions, generics
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import RegisterSerializer, LoginSerializer, PlayerSerializer, GameSerializer, GameJoinSerializer, GameMoveSerializer, GameMovesSerializer

from .game import ShogiGame
from .player import ShogiPlayer

from .models import Player, Game, GameStatus


OUR_PLAYER = 0
OPPONENT_PLAYER = 1


def reset_session(request):
    request.session.clear()
    return redirect('../game/')


def game_board(request):
    encoded_game = request.session.get('game')

    if encoded_game:
        game_bytes = base64.b64decode(encoded_game)
        game = pickle.loads(game_bytes)
    else:
        game = ShogiGame(ShogiPlayer("Gojo Satoru", 1), ShogiPlayer("Geto Suguru", -1))
        

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


class RuleAPIView(views.APIView):
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
    

class RegisterView(views.APIView):
    @swagger_auto_schema(      
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='username'
                ),
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='email'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='password'
                ),
                'password2': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='password2'
                )
            }
        )
    )

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Registeration successful!"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(views.APIView):
    @swagger_auto_schema( 
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='username'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='password'
                )
            }
        )
    )

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if user:
            login(request, user)
            return Response({"datail": "Login successful!"}, status=status.HTTP_200_OK)
        
        return Response({"datail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    

class LogoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        logout(request)
        return Response({"detail": "Logged out successfully!"})
    

class CheckLoginStatusView(views.APIView):
    def get(self, request, format=None):
        user = request.user
        if user and user.is_authenticated:
            return Response({'status': 'Logged in', 'user': user.username})
        return Response({'status': 'Not logged in'}, status=status.HTTP_401_UNAUTHORIZED)
    

class PlayerView(generics.RetrieveAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        username = self.kwargs.get('username')
        try:
            return Player.objects.get(user__username=username)
        except Player.DoesNotExist:
            raise exceptions.NotFound("Player does not found")


class GameCreateView(generics.CreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def perform_create(self, serializer):
        # 設定 our_player
        player, _ = Player.objects.get_or_create(user=self.request.user)

        our_player = ShogiPlayer(player.user.username, 1)
        shogi_game = ShogiGame(our_player)
        
        serializer.validated_data['our_player'] = player
        serializer.validated_data['binary_game'] = pickle.dumps(shogi_game)

        # 最後保存遊戲到數據庫
        serializer.save()

class GameDetailDeleteView(generics.RetrieveDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    lookup_field = 'uid'


class GameListView(generics.ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    lookup_field = 'uid'


class GameMovesView(generics.RetrieveAPIView):
    queryset = Game.objects.all()
    serializer_class = GameMovesSerializer
    lookup_field = 'uid'


class GameJoinView(generics.UpdateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameJoinSerializer
    lookup_field = 'uid'

    def update(self, request, *args, **kwargs):
        # 從 Request Body 中提取 game_id
        game_uid = request.data.get('uid')
        if not game_uid:
            return Response({'detail': 'Game ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 根據 game_uid 獲取遊戲實例
        try:
            game = Game.objects.get(uid=game_uid)
        except Game.DoesNotExist:
            return Response({'detail': 'Game is not found.'}, status=status.HTTP_404_NOT_FOUND)

        # 檢查遊戲是否已有對手
        if game.opponent_player:
            return Response({'detail': 'Game has already an opponent.'}, status=status.HTTP_400_BAD_REQUEST)
        
        player, _ = Player.objects.get_or_create(user=request.user)

        # 檢查我方與敵方玩家是否為同一人
        if player == game.our_player:
            return Response({'detail': 'our_player isn\'t equal to opponent_player.'}, status=status.HTTP_400_BAD_REQUEST)
        game.opponent_player = player

        shogi_game = pickle.loads(game.binary_game)

        # Set opponent_player to shogi_game: 新增敵方玩家到將棋類別
        opponent_player = ShogiPlayer(player.user.username, -1)
        shogi_game.players[OPPONENT_PLAYER] = opponent_player
        shogi_game.board.opponent_player = opponent_player

        print(shogi_game.board)

        shogi_board_data = {
            "our_player": shogi_game.players[OUR_PLAYER].name,
            "opponent_player": shogi_game.players[OPPONENT_PLAYER].name,
            "Current board": str(shogi_game.board)
        }

        game.binary_game = pickle.dumps(shogi_game)
        game.save()

        return Response(shogi_board_data, status=status.HTTP_200_OK)
    

class GameMoveView(generics.UpdateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameMoveSerializer
    lookup_field = 'uid'

    def update(self, request, *args, **kwargs):
        # 從 Request Body 中提取 game_id
        game_uid = request.data.get('uid')
        if not game_uid:
            return Response({'detail': 'Game ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 根據 game_uid 獲取遊戲實例
        try:
            game = Game.objects.get(uid=game_uid)
        except Game.DoesNotExist:
            return Response({'detail': 'Game not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if game.status == GameStatus.FINISHED:
            return Response({'detail': 'The game is over.'}, status=status.HTTP_400_BAD_REQUEST)
        
        shogi_game = pickle.loads(game.binary_game)

        shogi_game.current_player = shogi_game.players[shogi_game.game_round % 2]

        # 檢查玩家是否是遊戲的一部分
        shogi_players_name = [player.name for player in shogi_game.players]
        if request.user.username not in shogi_players_name:
            return Response({'detail': 'Not a part of this game.'}, status=status.HTTP_403_FORBIDDEN)
        
        # TODO: 檢查是否是該玩家的回合（之後會用 WebSocket，主要是先能自我對弈）

        # 執行棋步，並更新遊戲狀態，如果例外會回傳 400
        try:
            move = request.data.get('move')
            shogi_game.board.execute_move(move, shogi_game.current_player)
            game.game_record += f"{move} "
            shogi_game.game_round += 1
        except Exception as e:
            return Response({'detail': e}, status=status.HTTP_400_BAD_REQUEST)
        
        print(shogi_game.board)
        
        result = shogi_game.get_game_ended(shogi_game.players[OUR_PLAYER], shogi_game.players[OPPONENT_PLAYER])
        if result:
            if result == 1:
                winner = game.our_player
            else:
                winner = game.opponent_player

            game.end_game(winner)

            return Response({'detail': 'Game over'}, status=status.HTTP_200_OK)
        
        shogi_board_data = {
            "Next_game_round": shogi_game.game_round + 1,
            "Next_player": shogi_game.current_player.name,
            "Current board": str(shogi_game.board)
        }
        
        # 如果棋步是合法的，保存遊戲的變動
        game.binary_game = pickle.dumps(shogi_game)
        game.save()

        return Response(shogi_board_data, status=status.HTTP_200_OK)