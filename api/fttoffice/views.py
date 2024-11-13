from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Task
from fttoffice.libs.Tools import Tools
from django.utils import timezone
import uuid
import logging
from datetime import datetime
from drf_yasg import openapi
from fttoffice.libs.VQIP_ipv6BlockByName import ipv6BlockByName
from fttoffice.libs.VQIP_addIPv6Subnet import add_IPv6_Subnet
from fttoffice.libs.VQIP_ModifyV6Subnet import ModifyV6Subnet
from fttoffice.libs.VQIP_RetrieveIPv6address import RetrieveIPv6Address
from fttoffice.libs.VQIP_DeleteIPv6Subnet import DeleteIPv6Subnet
from fttoffice.libs.VQIP_RetrieveIPv4address import RetrieveIPv4address
from fttoffice.libs.VQIP_DeleteIPv4Addr import DeleteIPv4Addr
from fttoffice.libs.VQIP_ConectionVQIP import ConectionVQIP
from fttoffice.libs.exceptError import errorKeyExcptions
from celery.result import AsyncResult
from fttoffice.libs.exceptError import WS_OBJECT_NAME_NOT_FOUND
from .tasks import ProcessIPv4Registration
from drf_yasg.utils import swagger_auto_schema
from .serializers import (
    CadastrarAprovisionamentoSerializer,
    ConsultaSerializer,
    DeleteSerializer,
    ConsultarTarefasSerializer,
    CadastroIpv6Serializer,
)


data_atual = datetime.now().strftime("%d_%m_%Y")
LOGS_DIR = f'fttoffice_log_{data_atual}.log'
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s',level=logging.DEBUG, filename=LOGS_DIR)

class CadastrarAprovisionamentoView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description='Exemplo de resposta de sucesso',
                examples={
                    'application/json': {
                        'task_id': '37ed8048-4e97-4bc9-81c5-98459348a298'
                    }
                }
            ),
            400: 'Bad Request',
            404: 'Não encontrado',
            500: 'Erro interno do servidor'
        },
        request_body=CadastrarAprovisionamentoSerializer,
        operation_description='''Esta funcionalidade consiste em aprovisionar um objeto IPv4 e IPv6 LAN/WAN para o assinante do serviço FTTOffice. As informações requeridas para esta funcionalidade são o "UF", "GPON_ID" e o "Elemento", atrelados ao assinante. O valor do parâmetro "UF" será repetido em todas as requisições API Rest de aprovisionamento de IPv4 e IPv6 LAN/WAN(CREATE)''',
    )

    def post(self, request):
        serializer = CadastrarAprovisionamentoSerializer(data=request.data)

        if serializer.is_valid():
            element = serializer.validated_data['elemento']
            gponid = serializer.validated_data['gponid']
            uf = serializer.validated_data['uf']

            existing_task = Task.objects.filter(
                elemento=element,
                gponid=gponid,
                uf=uf,
                status='PENDING'
            ).first()

            if existing_task:
                return Response({'detail': 'Os parâmetros já estão na fila de processamento.',
                                 'task_id': existing_task.task_id},
                                status=status.HTTP_200_OK)
            else:
                vqip_instance_consulta = RetrieveIPv4address()
                server_instance = ConectionVQIP()
                instance_tools = Tools()
                server = server_instance.servidor_disponivel()

                if server in instance_tools.retorna_excecao():
                    return Response({'detail': 'Servidores VitalQIP disponível',
                                     'errorKey': 'NoServersAvailable'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                Retrieve = vqip_instance_consulta.Retrieve_IPv4_address(server,
                    gponid, uf)

            if Retrieve and Retrieve['ipv4']:
                task = Task.objects.filter(
                    ipv4=Retrieve['ipv4']).order_by('-end_time').first()
                if task and task.task_id:
                    return Response({'detail': 'Ja existe aprovisionamento para os parametros passados',
                                     'errorKey': 'OBJECTS_EXIST_DUPLICATE_NAME',
                                    'task_id': task.task_id}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Ja existe aprovisionamento para os parametros passados',
                                     'errorKey': 'OBJECTS_EXIST_DUPLICATE_NAME'}, status=status.HTTP_200_OK)

            else:
                task_id = str(uuid.uuid4())
                task_result = ProcessIPv4Registration.apply_async(
                    args=[element, gponid, task_id, uf], kwargs={})

                current_time = timezone.now()
                start_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

                task_data = {
                    'task_id': task_id,
                    'elemento': element,
                    'subnet': None,
                    'ipv4': None,
                    'uf': uf,
                    'gponid': gponid,
                    'status': 'PENDING',
                    'start_time': start_time,
                    'end_time': None,
                    'traceback': None,
                }
                task = Task.objects.create(**task_data)
                return Response({'task_id': task_id}, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConsultarTarefasView(APIView):
    permission_classes = [IsAuthenticated]
    def __init__(self):
        self.instance_tools = Tools()
        self.instance_error = errorKeyExcptions()

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description='Exemplo de resposta de sucesso',
                examples={
                    'application/json': {
                        "elemento": "XXXXXX",
                        "gponid": "655-TESTEAPI",
                        "ipv4": "XXX",
                        "Subnet": "XXX",
                        "gponid_wan": "655-TESTEAPI_WAN",
                        "ipv6_wan": "XXXX",
                        "gponid_lan": "655-TESTEAPI_LAN",
                        "ipv6_lan": "XXXXX",
                        "Status": "ATIVO"
                    }
                }
            ),
            400: 'Bad Request',
            404: 'Não encontrado',
            500: 'Erro interno do servidor'
        },
        request_body=ConsultarTarefasSerializer,
        operation_description='''Esta funcionalidade consiste em consultar, no banco fttoffice_db as informações do objeto IPv4 e IPv6 LAN/WAN associados ao cliente do serviço FTTOffice. As informações requeridas para esta funcionalidade é "task_id" que são gerados ao cadastrar um novo IPV4 e IPv6 no endpoint "api/v2/CadastrarAprovisionamento/".'''
    )
    def post(self, request):
        serializer = ConsultarTarefasSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'detail': 'Tarefa não encontrada'}, status=status.HTTP_404_NOT_FOUND)

        task_id = serializer.validated_data['task_id']

        try:
            task = Task.objects.get(task_id=task_id)

            if task.status == 'ATIVO':
                response_data = {
                    'elemento': task.elemento,
                    'gponid': task.gponid,
                    'ipv4': task.ipv4 + f'/25',
                    # 'ipv4': task.ipv4 + f'/{ self.instance_tools.calcula_subnet_mask(task.subnet)}',
                    'Subnet': task.subnet,
                    'gponid_wan': task.gponid_wan,
                    'ipv6_wan': task.ipv6_wan,
                    'gponid_lan': task.gponid_lan,
                    'ipv6_lan': task.ipv6_lan,
                    'Status': task.status,                    
                }
                return Response(response_data, status=status.HTTP_200_OK)

            elif task.status == 'Deletado':
                response_data = {'ipv4': task.ipv4 + f'/25',
                                #  'ipv4': task.ipv4 + f'/{ self.instance_tools.calcula_subnet_mask(task.subnet)}',
                                 'Subnet': task.subnet,
                                 'gponid': task.gponid,
                                 'gponid_wan': task.gponid_wan,
                                 'ipv6_wan': task.ipv6_wan,
                                 'gponid_lan': task.gponid_lan,
                                 'ipv6_lan': task.ipv6_lan,
                                 'Data da Criação': task.start_time,
                                 'Data da Deleção': task.data_delecao,
                                 'Status': task.status,      
                                 'details': task.details
                                }
                return Response(response_data, status=status.HTTP_200_OK)

            elif task.status == 'FAILURE':
                
                error_exceptions = self.instance_error.handle_error(str(task.traceback))
                response_data = {'elemento': task.elemento,
                                 'gponid': task.gponid,
                                 'uf': task.uf,
                                 'Data da Criação': task.start_time,
                                 'details': error_exceptions['details'],
                                 "errorKey": error_exceptions['errorKey'],
                                 'Status': task.status
                                 }
                
                return Response(response_data, status=status.HTTP_200_OK)

        except WS_OBJECT_NAME_NOT_FOUND as e:
            return Response({'detail': f'GPONID não existe.',
                             'errorKey': f'{e}'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': f'Falha na chamada da API: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeletarAprovisionamentoView(APIView):
    permission_classes = [IsAuthenticated]
    def __init__(self):
        self.instance_tools = Tools()
        self.ErrorsKey_instance = errorKeyExcptions()
        self.instance_delete_ipv6 = DeleteIPv6Subnet()
        self.instance_delete_ipv4 = DeleteIPv4Addr()
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description='Exemplo de resposta de sucesso',
                examples={
                    'application/json': {
                        "details": {
                            "IPV4": "IPV4 Deletado com sucesso.",
                            "IPV6": "IPV6 Deletado com sucesso."
                        },
                        "task_id": "8fe10d3c-04c5-403e-930a-8efa68281451"
                    }
                }
            ),
            400: 'Bad Request',
            404: 'Não encontrado',
            500: 'Erro interno do servidor'
        },
        request_body=DeleteSerializer,
        operation_description='''Esta funcionalidade consiste na remoção, na plataforma Vital QIP, do objeto IPv4 e IPv6 LAN/WAN associados ao cliente do serviço FTTOffice. As informações requeridas para esta funcionalidade são o "UF" e o "GPONID" do objeto IPv4.'''
    )
    def delete(self, request):
        serializer = DeleteSerializer(data=request.data)

        if serializer.is_valid():
            gponid = serializer.validated_data['gponid']
            uf = serializer.validated_data['uf']
            

            try:
                task = Task.objects.filter(
                    gponid=gponid).order_by('-end_time').first()
            except Exception as e:
                return Response({'detail': f'Gponid inválido: {e}'}, status=status.HTTP_400_BAD_REQUEST)

            if not task:
                return Response({'details': 'Gponid não está cadastrado. Verifique o Gponid fornecido.'}, status=status.HTTP_404_NOT_FOUND)

            if task.status == 'Deletado':
                task.details = "Gponid encontra-se com status Deletado"
                return Response({'details': task.details,
                                'task_id': task.task_id}, status=status.HTTP_404_NOT_FOUND)

            try:
                response_ipv4 = self.instance_delete_ipv4.delete_IPv4(gponid, uf, task.task_id)
                response_ipv6_wan = self.instance_delete_ipv6.Delete_IPv6_Subnet(gponid+'_WAN', uf, '64')
                response_ipv6_lan = self.instance_delete_ipv6.Delete_IPv6_Subnet(gponid+'_LAN', uf, '56')
                print(f'IPV4: {response_ipv4}')
                print(f'IPV6_WAN: {response_ipv6_wan}')
                print(f'IPV6_LAN: {response_ipv6_lan}')


                if response_ipv4 and response_ipv6_wan and response_ipv6_lan == True:
                    current_time = timezone.now()
                    task.status = 'Deletado'
                    task.details = "IPV4 Deletado com sucesso."
                    task.data_delecao = current_time
                    task.save()
                    return Response({"details": {
                                    "IPV4": "IPV4 Deletado com sucesso.",
                                    "IPV6": "IPV6 Deletado com sucesso.",
                                    },
                                     'task_id': task.task_id}, status=status.HTTP_200_OK)
                
                elif response_ipv4 or response_ipv6_wan or response_ipv6_lan != True:
                    error_response_ipv4 = self.ErrorsKey_instance.handle_error_delete(response_ipv4)
                    error_response_ipv6_wan  =  self.ErrorsKey_instance.handle_error_delete(response_ipv6_wan)
                    error_response_ipv6_lan  =  self.ErrorsKey_instance.handle_error_delete(response_ipv6_wan)

                    print("Valor de error_response_ipv4:", error_response_ipv4)
                    print("Valor de error_response_ipv6_wan:", error_response_ipv6_wan)
                    print("Valor de error_response_ipv6_lan:", error_response_ipv6_lan)

                    if response_ipv4 == True and response_ipv6_wan != True:
                        return Response({
                            "details": {
                                "IPV4": "IPV4 Deletado com sucesso.",
                                "IPV6": error_response_ipv6_wan
                            },
                            'task_id': task.task_id}, status=status.HTTP_200_OK)

                    elif response_ipv4 != True and response_ipv6_wan == True:
                        return Response({
                            "details": {
                                "IPV4": error_response_ipv4,
                                "IPV6": "IPV6 Deletado com sucesso."
                            },
                            'task_id': task.task_id}, status=status.HTTP_200_OK)

                    elif response_ipv4 != True and response_ipv6_wan != True:
                        return Response({
                            "details": {
                                "IPV4": error_response_ipv4,
                                "IPV6": error_response_ipv6_wan
                            },
                            'task_id': task.task_id}, status=status.HTTP_200_OK)

                else:
                    task.data_delecao = None
                    task.details = 'Objeto GPONID foi delatado manualmente no VITAL QIP'
                    task.status = 'Deletado'
                    task.save()
                    return Response({'detail': task.details,
                                     'task_id': task.task_id}, status=status.HTTP_404_NOT_FOUND)



            except Exception as e:
                return Response({'detail': f'Falha na chamada da API: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HealthCheckView(APIView):
    def __init__(self):
        self.instance = Tools()
    @swagger_auto_schema(

        responses={
            200: openapi.Response(
                description='Exemplo de resposta de sucesso',
                examples={
                    'application/json': {
                        "fttoffice_api": "up",
                        "database": "up",
                        "queues": "up",
                        "cpu_usage_percent": 0.2,
                        "memory_usage_percent": 28.1
                    }
                }
            ),
            500: 'Erro interno do servidor'
        },
        operation_description='''Esta funcionalidade consiste em validar os serviços da api FTTOFFICE. Quando chamada com sucesso status 200(OK), ela retorna um dicionário de indicando quais serviços está funcionando corretamente. Em caso de falha será retonado o status "down" para o item que está sendo validado. Em caso de erro interno, um código de status 500 (Internal Server Error) será retornado. Esta é uma operação simples usada para monitorar a disponibilidade do serviço.'''
    )
    def get(self, request):

        database_is_healthy = self.instance.check_database_health()
        check_resource_usage = self.instance.check_resource_usage()
        print(check_resource_usage)
        task_id = self.instance.get_valid_task_id()
        print(f"task_id: {task_id}")

        if task_id:
            check_async_tasks_health = self.instance.check_async_tasks_health(
                task_id)
        else:
            check_async_tasks_health = False

        response_data = {
            'fttoffice_api': 'up',
            'database': 'up' if database_is_healthy else 'down',
            'queues': 'up' if check_async_tasks_health else 'down',
            'cpu_usage_percent': check_resource_usage['cpu_usage_percent'] if check_resource_usage else 'down',
            'memory_usage_percent': check_resource_usage['memory_usage_percent'] if check_resource_usage else 'down',
        }

        return Response(response_data, status=200)


class ConsultarAprovisionamentoIPv4View(APIView):
    permission_classes = [IsAuthenticated]
    def _init__(self):
        self.instance = Tools()
    @swagger_auto_schema(auto_schema=None)
    def post(self, request):
        serializer = ConsultaSerializer(data=request.data)

        if serializer.is_valid():
            gponid = serializer.validated_data['gponid']
            uf = serializer.validated_data['uf']
            vqip_instance_consulta = RetrieveIPv4address()
            server_instance = ConectionVQIP()
            server = server_instance.servidor_disponivel()

            try:
                Retrieve = vqip_instance_consulta.Retrieve_IPv4_address(server,
                    gponid, uf)
                if Retrieve is None:
                    return Response({'detail': 'Não existe IPv4 para o GPONID informado.',
                                     'errorKey': 'WS_OBJECT_NAME_NOT_FOUND'}, status=status.HTTP_404_NOT_FOUND)

                print(Retrieve)
                response = {
                    'ipv4': Retrieve['ipv4'],
                    'gponid': Retrieve['gponid']
                }
                return Response(response, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'detail': f'Falha na chamada da API: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CadastroAprovisionamentoIPV6View(APIView):
    permission_classes = [IsAuthenticated]
    def __init__(self):
        self.block_by_name_instance = ipv6BlockByName()
        self.addI_ipv6_subnet_instance = add_IPv6_Subnet()
        self.ErrorsKey_instance = errorKeyExcptions()
        self.instance_Tools = Tools()

    @swagger_auto_schema(auto_schema=None)
    def post(self, request):
        serializer = CadastroIpv6Serializer(data=request.data)

        if serializer.is_valid():
            element = serializer.validated_data['elemento']
            gponid = serializer.validated_data['gponid']
            uf = serializer.validated_data['uf']

            try:
                # IPv6 block by Name and poolName | Pesquisa de Bloco
                BlockByName_response = self.block_by_name_instance.ipv6_block_by_name(
                    element, uf)

                error_response  =  self.ErrorsKey_instance.handle_error(BlockByName_response)

                if error_response:  
                    print('caindo aqui')
                    print(error_response)
                    return error_response
                
                print(BlockByName_response)

                # add IPv6Subnet ALGORITHM | Informações do bloco
                # CHAMADA WAN
                add_subnet_wan  = self.addI_ipv6_subnet_instance.add_IPv6_Subnet(
                    element=BlockByName_response['poolName'],
                    parentPool=BlockByName_response['parentPool'],
                    blockAddress=BlockByName_response['address'], 
                    subnetPrefixLength='64',
                    uf=uf)
                
                print(f'WAN: {add_subnet_wan}')

                error_response  =  self.ErrorsKey_instance.handle_error(add_subnet_wan)

                if error_response:  
                     return Response({error_response}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                                
                # CHAMADA LAN
                add_subnet_lan  = self.addI_ipv6_subnet_instance.add_IPv6_Subnet(
                    element=BlockByName_response['poolName'],
                    parentPool=BlockByName_response['parentPool'],
                    blockAddress=BlockByName_response['address'], 
                    subnetPrefixLength='56',
                    uf=uf)
                
                print(f'LAN: {add_subnet_lan }')

                error_response  =  self.ErrorsKey_instance.handle_error(add_subnet_lan)

                if error_response:
                     return Response({error_response}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                address_ipv6_WAN =  self.instance_Tools.extrair_endereco_ipv6(add_subnet_wan)
                address_ipv6_LAN =  self.instance_Tools.extrair_endereco_ipv6(add_subnet_lan )

                print(f'WAN: {address_ipv6_WAN}')
                print(f'LAN: {address_ipv6_LAN}')

                # MODIFY V6 SUBNET | Altera Nome e endereço da Subnet Alocada
                gponid_wan =  gponid + '_WAN'
                gponid_lan =  gponid + '_LAN'
                ModifyV6Subnet_instance = ModifyV6Subnet()

                change_name_WAN = ModifyV6Subnet_instance.Modify_V6_Subnet(
                    gponid_wan, address_ipv6_WAN, uf, element, '64'
                )

                error_response  =  self.ErrorsKey_instance.handle_error(change_name_WAN)

                if error_response:
                    return error_response
                
                change_name_LAN = ModifyV6Subnet_instance.Modify_V6_Subnet(
                    gponid_lan, address_ipv6_LAN, uf, element, '56'
                )

                error_response  =  self.ErrorsKey_instance.handle_error(change_name_LAN)

                if error_response:
                     return Response({error_response}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                if change_name_WAN == 'SUCESSO' and change_name_LAN == 'SUCESSO':
                    print(f'WAN: {change_name_WAN}')
                    print(f'LAN: {change_name_LAN}')
                
                else:
                    print(f'WAN: {change_name_WAN}')
                    print(f'LAN: {change_name_LAN}')

                response = {
                    'elemento': element,
                    'gponid_wan': gponid_wan,
                    'ipv6_wan': address_ipv6_WAN,
                    'gponid_lan': gponid_lan,
                    'ipv6_lan': address_ipv6_LAN
                }

                return Response(response, status=status.HTTP_200_OK)                  

            except Exception as e:
                return Response({'detail': f'Falha na chamada da API: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
