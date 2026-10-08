from decimal import Decimal

from django.contrib.auth import authenticate, get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Oyente, Pago
from .notify import avisar_oyentes
from .serializers import (
    EmisorSerializer,
    OyenteSerializer,
    PagoSerializer,
    RegistroSerializer,
)

User = get_user_model()


def _respuesta_token(user):
    token, _ = Token.objects.get_or_create(user=user)
    return {"token": token.key, "username": user.username}


# ── Auth ──────────────────────────────────────────────────────────────────────


@api_view(["POST"])
@permission_classes([AllowAny])
def registro(request):
    s = RegistroSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    user = User.objects.create_user(
        username=s.validated_data["username"], password=s.validated_data["password"]
    )
    return Response(_respuesta_token(user), status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = str(request.data.get("username", "")).strip().lower()
    password = str(request.data.get("password", ""))
    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {"detail": "Usuario o contraseña incorrectos."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response(_respuesta_token(user))


# ── Mis oyentes ───────────────────────────────────────────────────────────────


class OyenteListCreate(generics.ListCreateAPIView):
    serializer_class = OyenteSerializer

    def get_queryset(self):
        return (
            Oyente.objects.filter(emisor=self.request.user)
            .select_related("oyente")
            .order_by("oyente__username")
        )

    def create(self, request, *args, **kwargs):
        username = str(request.data.get("username", "")).strip()
        oyente = User.objects.filter(username__iexact=username).first()
        if oyente is None:
            raise ValidationError({"detail": f"No existe el usuario '{username}'."})
        if oyente == request.user:
            raise ValidationError({"detail": "No puedes agregarte a ti mismo."})
        relacion, creada = Oyente.objects.get_or_create(
            emisor=request.user,
            oyente=oyente,
            defaults={"ver_historial": bool(request.data.get("ver_historial", False))},
        )
        if not creada:
            raise ValidationError({"detail": f"'{oyente.username}' ya te escucha."})
        return Response(OyenteSerializer(relacion).data, status=status.HTTP_201_CREATED)


class OyenteDetail(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = OyenteSerializer
    http_method_names = ["patch", "delete"]

    def get_queryset(self):
        return Oyente.objects.filter(emisor=self.request.user)


# ── A quiénes escucho ─────────────────────────────────────────────────────────


class EmisorList(generics.ListAPIView):
    serializer_class = EmisorSerializer

    def get_queryset(self):
        return (
            Oyente.objects.filter(oyente=self.request.user)
            .select_related("emisor")
            .order_by("emisor__username")
        )


@api_view(["GET"])
def pagos_de_emisor(request, username):
    relacion = get_object_or_404(
        Oyente, oyente=request.user, emisor__username__iexact=username
    )
    if not relacion.ver_historial:
        raise PermissionDenied(f"{relacion.emisor.username} no comparte su historial.")
    return Response(_resumen_pagos(relacion.emisor))


# ── Pagos que sube el celular emisor ──────────────────────────────────────────


def _resumen_pagos(emisor):
    """Total de hoy + últimos 100 pagos de `emisor`."""
    pagos = Pago.objects.filter(emisor=emisor)
    hoy = timezone.localdate()
    total_hoy = pagos.filter(fecha__date=hoy).aggregate(t=Sum("monto"))["t"] or Decimal("0")
    return {
        "total_hoy": str(total_hoy),
        "pagos": PagoSerializer(pagos[:100], many=True).data,
    }


@api_view(["GET", "POST"])
def pagos(request):
    """GET: mis pagos (pantalla de inicio). POST: el celular sube un pago detectado."""
    if request.method == "GET":
        return Response(_resumen_pagos(request.user))

    s = PagoSerializer(data=request.data)
    # El celular puede reenviar el mismo pago (reintentos): si ya existe, no se duplica
    # ni se vuelve a avisar.
    id_local = request.data.get("id_local")
    existente = Pago.objects.filter(id_local=id_local).first() if id_local else None
    if existente is not None:
        return Response(PagoSerializer(existente).data, status=status.HTTP_200_OK)

    s.is_valid(raise_exception=True)
    pago = s.save(emisor=request.user)
    avisar_oyentes(pago)
    return Response(PagoSerializer(pago).data, status=status.HTTP_201_CREATED)
