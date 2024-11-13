from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from django.urls import re_path
from fttoffice import views
from django.contrib import admin
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="FTTOFFICE_API",
        default_version="v2",
        description="""A API de aprovisionamento para o Serviço FTTOFFICE permite a integração com o sistemas de aprovisionamento de Service Order Management para obtenção de informações e gestão de endereços IPs destinados à configuração de clientes. Esta documentação descreve o uso da API e os procedimentos para solicitar e liberar IPs por meio desta integração.

Requisitos de Autenticação:
Para utilizar esta API, é necessário autenticar-se por meio de credenciais fornecidas pela equipe de Automação e RPA da engenharia. A autenticação é realizada por meio de um token de acesso único.

Recursos Disponíveis:
A API fornece os seguintes recursos para gerenciamento de IPs:

Cadastro de IPV4 e IPV6:
Endpoint: /api/v2/CadastrarAprovisionamento/
Método: POST
Descrição: Retorna a lista de subnets disponíveis para uma organização (SER) específica e reserva um IPV4 e IPV6 LAN/WAN disponível em uma subnet específica para um cliente. Requer os parâmetros necessários para identificar a subnet e o cliente.

Consulta IPV4 e IPV6:
Endpoint: /api/v2/ConsultarAprovisionamento/
Método: POST
Descrição: Consulta um objeto IPV4 e IPV6 LAN/WAN associado a um cliente expecifico.

Liberar IP:
Endpoint: /api/v2/DeletarAprovisionamento/
Método: DELETE
Descrição: Libera IPV4 e IPV6 LAN/WAN previamente reservado para um cliente. Requer os parâmetros necessários para identificar o cliente e o IP a ser liberado.

Resposta:
A resposta bem-sucedida retornará um código de status 200 e uma confirmação da reserva do IP para ser consultada em 60s após a reserva.. Em caso de erro, será fornecido um código de erro e uma mensagem explicativa.

Considerações Adicionais:

A API de aprovisionamento está disponível em formato REST para integração.
Para garantir a segurança e integridade dos dados, todas as solicitações devem ser feitas por meio de conexões seguras (HTTP).
Recomenda-se a leitura cuidadosa da documentação técnica para compreender completamente os métodos disponíveis e seus parâmetros.
Esta documentação fornece uma visão geral dos principais recursos da API de aprovisionamento para o Serviço FTTOFFICE. Para obter informações detalhadas sobre cada recurso e exemplos de solicitação, consulte  o time de Automação e RPA da engenharia.""",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="esdras.moreira@vtal.com"),
        # license=openapi.License(name="Licença Example"),
        security=[{'BearerAuth': []}],
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # ADMIN
    path('secureadmin/', admin.site.urls),
    # Endpoint API FTTOFFICE
    path('api/v2/CadastrarAprovisionamento/',
         views.CadastrarAprovisionamentoView.as_view(), name='Cadastrar_Aprovisionamento'),
    path('api/v2/DeletarAprovisionamento/',
         views.DeletarAprovisionamentoView.as_view(), name='Delete_Aprovisionamento'),
    path('api/v2/ConsultarAprovisionamento/',
         views.ConsultarTarefasView.as_view(), name='Consultar_AprovisionamentoDB'),
    path('api/v1/CadastrarAprovisionamentoIPV6/',
         views.CadastroAprovisionamentoIPV6View.as_view(), name='Cadastrar_Aprovisionamento_IPV6'),
    path('api/v1/ConsultarAprovisionarmentoIPV4/',
         views.ConsultarAprovisionamentoIPv4View.as_view(), name='Consultar_Aprovisionamento_IPV4'),
    path('api/v2/health/', views.HealthCheckView.as_view(), name='health_check'),
    # Token JWT
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    # Swagger Documentation
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0),
         name='schema-json'),

]
