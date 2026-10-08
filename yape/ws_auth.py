from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def _usuario_por_token(key):
    from rest_framework.authtoken.models import Token

    try:
        return Token.objects.select_related("user").get(key=key).user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    """Autentica el WebSocket con ?token=<token DRF> en la URL."""

    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get("query_string", b"").decode())
        key = (query.get("token") or [None])[0]
        scope["user"] = await _usuario_por_token(key) if key else AnonymousUser()
        return await super().__call__(scope, receive, send)
