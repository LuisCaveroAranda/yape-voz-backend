import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .notify import grupo_usuario

log = logging.getLogger("yape")


class PagosConsumer(AsyncJsonWebsocketConsumer):
    """Conexión permanente del celular oyente: recibe los pagos de quienes escucha."""

    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close(code=4401)
            return
        self.grupo = grupo_usuario(user.id)
        await self.channel_layer.group_add(self.grupo, self.channel_name)
        await self.accept()
        log.info("WebSocket conectado: %s", user.username)

    async def disconnect(self, code):
        if hasattr(self, "grupo"):
            await self.channel_layer.group_discard(self.grupo, self.channel_name)

    async def pago_nuevo(self, event):
        await self.send_json(event["data"])
