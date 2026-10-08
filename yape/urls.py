from django.urls import path

from . import views

urlpatterns = [
    path("auth/registro/", views.registro),
    path("auth/login/", views.login),
    path("oyentes/", views.OyenteListCreate.as_view()),
    path("oyentes/<int:pk>/", views.OyenteDetail.as_view()),
    path("escucho/", views.EmisorList.as_view()),
    path("escucho/<str:username>/pagos/", views.pagos_de_emisor),
    path("pagos/", views.crear_pago),
]
