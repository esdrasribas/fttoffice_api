from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from fttoffice import views
from django.contrib import admin

urlpatterns = [
    path('secureadmin/', admin.site.urls),
    path('api/v1/CadastrarAprovisionamentoIPV4/', views.CadastrarAprovisionamentoIPv4View.as_view(), name='Cadastrar_Aprovisionamento_IPV4'),
    path('api/v1/ConsultarAprovisionarmentoIPV4/', views.ConsultarAprovisionamentoIPv4View.as_view(), name='Consultar_Aprovisionamento_IPV4'),
    path('api/v1/DeletarAprovisionamentoIPv4/', views.DeletarAprovisionamentoIPv4View.as_view(), name='Delete_IPv4_Addr'),
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
]

