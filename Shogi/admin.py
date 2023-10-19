from django.contrib import admin
from Shogi import models

# Register your models here.
admin.site.register(models.Player)
admin.site.register(models.Game)
admin.site.register(models.Move)