from django.contrib import admin
from Shogi.models import Player
from Shogi.models import Game
from Shogi.models import Move

# Register your models here.
admin.site.register(Player)
admin.site.register(Game)
admin.site.register(Move)