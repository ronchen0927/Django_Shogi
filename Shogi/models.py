import uuid
from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return self.user.username

class GameStatus(models.TextChoices):
    ONGOING = "Ongoing", "Ongoing"
    FINISHED = "Finished", "Finished"

class Game(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    our_player = models.ForeignKey(Player, related_name="game_as_our_player", null=True, on_delete=models.SET_NULL)
    opponent_player = models.ForeignKey(Player, related_name="game_as_opponent_player", null=True, on_delete=models.SET_NULL)
    winner = models.ForeignKey(Player, related_name="games_won", null=True, on_delete=models.SET_NULL)
    loser = models.ForeignKey(Player, related_name="games_lost", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=10, choices=GameStatus.choices, default=GameStatus.ONGOING)
    game_record = models.TextField(default="")
    binary_game = models.BinaryField(default=b"")
    timestamp = models.DateTimeField(auto_now_add=True)

    def end_game(self, winner):
        # 檢查遊戲是否已有結果
        if self.status == GameStatus.FINISHED:
            raise ValueError("This game has already finished. Cannot set the result again.")

        self.status = GameStatus.FINISHED
        self.winner = winner
        if winner == self.our_player:
            self.loser = self.opponent_player
        else:
            self.loser = self.our_player

        self.save()