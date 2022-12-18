from django.urls import re_path
from . import consumers

websocket_patterns = [
    re_path(r'ws/update/(?P<room_name>\w+)/(?P<token>\w+)/$', consumers.DocConsumer.as_asgi())
]