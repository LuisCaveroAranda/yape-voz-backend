import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Oyente, Pago

User = get_user_model()

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.]{3,30}$")


class RegistroSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(min_length=6, write_only=True)

    def validate_username(self, value):
        value = value.strip().lower()
        if not USERNAME_RE.match(value):
            raise serializers.ValidationError(
                "Usa de 3 a 30 letras, números, punto o guion bajo."
            )
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Ese usuario ya existe.")
        return value


class OyenteSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="oyente.username", read_only=True)

    class Meta:
        model = Oyente
        fields = ["id", "username", "ver_historial"]


class EmisorSerializer(serializers.ModelSerializer):
    """Visto desde el oyente: a quién escucha y si puede ver su historial."""

    username = serializers.CharField(source="emisor.username", read_only=True)

    class Meta:
        model = Oyente
        fields = ["username", "ver_historial"]


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ["id_local", "remitente", "monto", "fecha"]
