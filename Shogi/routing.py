from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"wss/game/(?P<game_uid>[^/]+)/$", consumers.GameConsumer.as_asgi()),
]