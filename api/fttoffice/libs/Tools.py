import random
from django.db import connection
from ..models import Task
from django.utils import timezone
import re
from celery.result import AsyncResult
import psutil


class Tools:
    def __init__(self):
        self.used_subnets = set()
        self.used_addresses = set()

    # Seleciona uma subnet valida:
    def get_subnet(self, subnet_info_list, task_id):

        available_subnets = [
            subnet_info for subnet_info in subnet_info_list if subnet_info['subnetAddress'] not in self.used_subnets
        ]

        if not available_subnets:
            return 'IPV4_OBJECT_NOT_FOUND'

        subnet_info = random.choice(available_subnets)
        subnet_address = subnet_info['subnetAddress']
        subnet_mask = subnet_info['subnetMask']

        self.used_subnets.add(subnet_address)
        print(f"Subnet escolhida: {subnet_address} / Máscara: {subnet_mask}")

        return subnet_info

    def get_name_and_poll(self, name_and_polls_list):

        available_name_and_polls = [
            np_info for np_info in name_and_polls_list if np_info['address'] not in self.used_addresses
        ]

        if not available_name_and_polls:
            print("Não há mais name_and_polls disponíveis.")
            return None

        np_info = random.choice(available_name_and_polls)
        address = np_info['address']
        prefixLength = np_info['prefixLength']
        pool_name = np_info['poolName']
        parent_pool = np_info['parentPool']

        self.used_addresses.add(address)
        print(
            f"Name_and_poll escolhido: {address} / prefixLength: {prefixLength} / PoolName: {pool_name} / ParentPool: {parent_pool}")

        return np_info

    # Valida se o endereço de IPV4 é válido:
    def valida_ip(self, ip):
        if ip is None:
            return False

        partes = ip.split(".")
        ultimo_octeto = partes[-1]

        if ultimo_octeto != "0":
            return True
        else:
            return False

    # Identifica qual o barrametno da submask
    def validaNetMask(self, subnetMask):
        netmask = {

        }

        if subnetMask in netmask:
            return netmask[subnetMask]
        

    # Obtém a região com a UF informada.
    def valida_regiao(self, uf):
        regiao1 = ["AL", "AM", "AP", "BA", "CE", "ES", "MA", "MG",
                   "PA", "PB", "PE", "PI", "RJ", "RN", "RR", "SE", "SP"]
        regiao2 = ["AC", "DF", "GO", "MS", "MT", "PR", "RO", "RS", "SC", "TO"]

        if uf in regiao1:
            organization = {
                "regiao_ipv4": "OI_Regiao_1",
                "regiao_ipv6": "OI_Regiao_1",
                "dominio": "ftto.vtal.net.br"
            }
            return organization

        elif uf in regiao2:
            organization = {
                "regiao_ipv4": "OI_Regiao_2",
                "regiao_ipv6": "Oi_Regiao_2",
                "dominio": "ftto.brasiltelecom.net.br"
            }
            return organization
        else:
            return "UF não existe"

    # HC Banco de dados
    def check_database_health(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    return True
        except Exception as e:
            print(f"Database check failed: {e}")
        return False

    # HC recursos utilizados
    def check_resource_usage(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent

        if cpu_usage > 90 or memory_usage > 90:
            return False
        return {
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": memory_usage,
        }

    # HC das tarefas celery
    def check_async_tasks_health(self, task_id):
        try:
            task = Task.objects.get(task_id=task_id)

            if task.status == 'ATIVO':
                return True
            else:
                return False
        except Exception as e:
            print(f"Async task check failed: {e}")
            return False

    # Consulta o banco de dados para obter o primeiro task_id com status 'ATIVO'
    def get_valid_task_id(self):
        try:

            task = Task.objects.filter(status='ATIVO').order_by('id').first()
            print(task.task_id)

            if task:
                return task.task_id
            else:
                return None
        except Exception as e:
            print(f"Error fetching a valid task_id: {e}")
            return None

    # Extrai enderço IPV6_WAN/LAN

    def extrair_endereco_ipv6(self, xml_soup):
        warning_message = xml_soup.find('ns1:warningMessage')
        if warning_message:

            text = warning_message.get_text()
            print(text)

            ipv6_regex = re.compile(
                r'(?<![:.\w])(?:[a-fA-F0-9]{0,4}:){1,7}[a-fA-F0-9]{0,4}::')

            matches = ipv6_regex.findall(text)
            return matches[0] if matches else None
        else:
            print('Não encontrado IPV6 no XML')
            return None

    def retorna_excecao(self):
        error_Key_Exception = ['IPV4_INVALID_ADDRESS',
                               'IPV4_OBJECT_NOT_FOUND',
                               'CLI_INVALID_IPV4_ADDRESS',
                               'GUI_IPV4_ADD_FAILED',
                               'ELEMENT_SUBNET_DOES_NOT_EXIST',
                               'WS_OBJECT_NAME_NOT_FOUND',
                               'WS_SUBNET_NOT_UNIQUE',
                               'WS_BLOCK_NOT_FOUND',
                               'WS_SUBNET_NOT_FOUND',
                               'IP_INVALID_V6_ADDRESS',
                               'IPV4_INVALID_ADDRESS',
                               'OBJECTS_EXIST_DUPLICATE_NAME',
                               'V4_OBJECT_NOT_FOUND_BY_ADDRESS',
                               'WS_OBJECT_NAME_NOT_FOUND',
                               'NoServersAvailable',
                               'UNKNOWN_ERROR']
        return error_Key_Exception

    def valida_excecao_delete(self):
        error_Key_Exception = ['Falha ao deletar o IPV6: WS_SUBNET_NOT_FOUND',
                               'Falha ao deletar o IPV4: WS_OBJECT_NAME_NOT_FOUND',
                               'Subnet não é unica. : WS_SUBNET_NOT_UNIQUE']
        return error_Key_Exception
    

