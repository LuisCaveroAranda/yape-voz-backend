from django.urls import path

from .consumers import PagosConsumer

websocket_urlpatterns = [
    path("ws/pagos/", PagosConsumer.as_asgi()),
]
