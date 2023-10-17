from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=100)
    victories = models.PositiveIntegerField(default=0)
    opponents = models.ManyToManyField(
        'self', 
        through='Game', 
        symmetrical=False, 
        related_name="opponents_played",
        through_fields=('player1', 'player2')
    )


class Game(models.Model):
    player1 = models.ForeignKey(Player, related_name="games_as_player1", on_delete=models.CASCADE)
    player2 = models.ForeignKey(Player, related_name="games_as_player2", on_delete=models.CASCADE)
    winner = models.ForeignKey(Player, related_name="games_won", null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.winner:
            self.winner.victories += 1
            self.winner.save()


class Move(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    description = models.TextField()  # 描述此手棋的動作
    timestamp = models.DateTimeField(auto_now_add=True)