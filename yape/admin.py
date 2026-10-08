from django.contrib import admin

from .models import Oyente, Pago


@admin.register(Oyente)
class OyenteAdmin(admin.ModelAdmin):
    list_display = ("emisor", "oyente", "ver_historial", "creado")


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("emisor", "remitente", "monto", "fecha")
    list_filter = ("emisor",)
