from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from unittest.mock import patch

from .game import ShogiGame
from .player import ShogiPlayer
from .models import Player, Game

import pickle

class CheckLoginStatusViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')


    def test_check_login_api_view(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        url = reverse('check-login')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'status': 'Not logged in'})

        self.client.login(username='testuser', password='password')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'Logged in', 'user': self.user.username})


class GameCreateViewTest(TestCase):
    def setUp(self):
        self.our_user = User.objects.create_user('our_user', 'our_user@example.com', 'password')
        self.our_player = Player.objects.create(user=self.our_user)

    def test_games_create_api_view(self):
        self.assertEqual(Player.objects.count(), 1)
        self.assertTrue(Player.objects.filter(user=self.our_user).exists())

        self.client.login(username='our_user', password='password')
        user_id = self.client.session['_auth_user_id']
        logged_in_user = get_user_model().objects.get(id=user_id)
        self.assertEqual(logged_in_user.username, 'our_user')

        url = reverse('game-create')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)


class GameJoinViewTest(TestCase):
    def setUp(self):
        self.our_user = User.objects.create_user('our_user', 'our_user@example.com', 'password')
        self.opponent_user = User.objects.create_user('opponent_user', 'opponent_user@example.com', 'password')
        self.our_player = Player.objects.create(user=self.our_user)
        self.opponent_player = Player.objects.create(user=self.opponent_user)

        our_player = ShogiPlayer(self.our_player.user.username, 1)  # obj our_player
        opponent_player = ShogiPlayer(self.opponent_player.user.username, -1)  # obj opponent_player

        shogi_game = ShogiGame(our_player, opponent_player)
        self.game = Game.objects.create(uid="74bf3f51-2c02-4cb0-aaa2-b9e8cc74cbd7", our_player=self.our_player, binary_game=pickle.dumps(shogi_game))
    
    def test_games_join_api_view(self):
        self.assertEqual(Player.objects.count(), 2)
        self.assertTrue(Player.objects.filter(user=self.our_user).exists())
        self.assertTrue(Player.objects.filter(user=self.opponent_user).exists())

        self.assertEqual(Game.objects.count(), 1)

        # Login opponent_player
        self.client.login(username='opponent_user', password='password')
        user_id = self.client.session['_auth_user_id']
        logged_in_user = get_user_model().objects.get(id=user_id)
        self.assertEqual(logged_in_user.username, 'opponent_user')

        url = reverse('game-join')
        put_data = {
            "uid": self.game.uid,
        }
        response = self.client.put(url, put_data, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["our_player"], self.our_player.user.username)
        self.assertEqual(response.json()["opponent_player"], self.opponent_player.user.username)


class GamesMoveViewTest(TestCase):
    def setUp(self):
        self.our_user = User.objects.create_user('our_user', 'our_user@example.com', 'password')
        self.opponent_user = User.objects.create_user('opponent_user', 'opponent_user@example.com', 'password')
        self.our_player = Player.objects.create(user=self.our_user)
        self.opponent_player = Player.objects.create(user=self.opponent_user)

        our_player = ShogiPlayer(self.our_player.user.username, 1)  # obj our_player
        opponent_player = ShogiPlayer(self.opponent_player.user.username, -1)  # obj opponent_player

        shogi_game = ShogiGame(our_player, opponent_player)
        self.game = Game.objects.create(our_player=self.our_player, opponent_player=self.opponent_player, binary_game=pickle.dumps(shogi_game))


    def test_games_move_api_view(self):
        self.assertEqual(Player.objects.count(), 2)
        self.assertTrue(Player.objects.filter(user=self.our_user).exists())
        self.assertTrue(Player.objects.filter(user=self.opponent_user).exists())

        self.assertEqual(Game.objects.count(), 1)

        # Test our_player and opponent_player move
        self.call_game_move(username='our_user', password='password', move='a3a4')
        self.call_game_move(username='opponent_user', password='password', move='b8e8')


    def call_game_move(self, username: str, password: str, move: str):
        self.client.login(username=username, password=password)
        user_id = self.client.session['_auth_user_id']
        logged_in_user = get_user_model().objects.get(id=user_id)
        self.assertEqual(logged_in_user.username, username)

        url = reverse('game-move')
        put_data = {
            "uid": self.game.uid,
            "move": move
        }
        
        # 使用 patch 來 mock async_to_sync 呼叫
        with patch('Shogi.views.async_to_sync') as mock_async:
            # 進行你的測試呼叫
            response = self.client.put(url, put_data, content_type='application/json')

            # 檢查響應狀態和其他需要驗證的內容
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['game_id'], str(self.game.uid))
            self.assertEqual(response.json()['move'], move)

            # 也可以驗證 async_to_sync 是否被呼叫
            mock_async.assert_called()