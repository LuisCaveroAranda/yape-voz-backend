import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

log = logging.getLogger("yape")


def grupo_usuario(user_id):
    return f"usuario_{user_id}"


def avisar_oyentes(pago):
    """Envía el pago por WebSocket a cada oyente del emisor que esté conectado."""
    layer = get_channel_layer()
    mensaje = {
        "type": "pago.nuevo",  # → PagosConsumer.pago_nuevo
        "data": {
            "tipo": "pago",
            "emisor": pago.emisor.username,
            "id_local": str(pago.id_local),
            "remitente": pago.remitente,
            "monto": str(pago.monto),
            "fecha": pago.fecha.isoformat(),
        },
    }
    oyente_ids = pago.emisor.oyentes.values_list("oyente_id", flat=True)
    for oyente_id in oyente_ids:
        async_to_sync(layer.group_send)(grupo_usuario(oyente_id), mensaje)
    log.info("Pago de %s avisado a %d oyente(s)", pago.emisor, len(oyente_ids))
