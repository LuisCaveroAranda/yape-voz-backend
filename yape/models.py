from django.conf import settings
from django.db import models


class Oyente(models.Model):
    """`oyente` puede escuchar los pagos que recibe `emisor`."""

    emisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="oyentes", on_delete=models.CASCADE
    )
    oyente = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="escucha_a", on_delete=models.CASCADE
    )
    ver_historial = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["emisor", "oyente"], name="oyente_unico"),
        ]

    def __str__(self):
        return f"{self.oyente} escucha a {self.emisor}"


class Pago(models.Model):
    emisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="pagos", on_delete=models.CASCADE
    )
    # id generado en el celular: si el celular reenvía el mismo pago, no se duplica.
    id_local = models.UUIDField(unique=True)
    remitente = models.CharField(max_length=80)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField()
    recibido = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        indexes = [models.Index(fields=["emisor", "-fecha"])]

    def __str__(self):
        return f"{self.emisor}: S/ {self.monto} de {self.remitente}"
