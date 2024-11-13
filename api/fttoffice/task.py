from fttoffice.libs.VQIP_ListOfSubnets import ListOfSubnets
from fttoffice.libs.VQIP_SelectNextFreeIPv4 import SelectNextFreeIPv4
from fttoffice.libs.VQIP_addIPv4Selected import addIPv4Selected
from .models import Task
from .libs.Tools import Tools
from django.db import transaction
from celery import shared_task
from django.utils import timezone
from celery.exceptions import SoftTimeLimitExceeded
from fttoffice.libs.exceptError import errorKeyExcptions
from fttoffice.libs.VQIP_ipv6BlockByName import ipv6BlockByName
from fttoffice.libs.VQIP_addIPv6Subnet import add_IPv6_Subnet
from fttoffice.libs.VQIP_ModifyV6Subnet import ModifyV6Subnet
from fttoffice.libs.VQIP_DeleteIPv6Subnet import DeleteIPv6Subnet
from fttoffice.libs.VQIP_DeleteIPv4Addr import DeleteIPv4Addr
from fttoffice.libs.VQIP_ConectionVQIP import ConectionVQIP


@shared_task
def ProcessIPv4Registration(element, gponid, task_id, uf):
    traceback_msg = None

    try:
        with transaction.atomic():
            # FLUXO DE CRIAÇÃO DO IPV4
            # Listando subnets:
            vqip_instance_List = ListOfSubnets()
            instance_tools = Tools()
            server_instance = ConectionVQIP()
            server = server_instance.servidor_disponivel()

            if server in instance_tools.retorna_excecao():
                traceback_msg = str(server)
                task = Task.objects.get(task_id=task_id)
                task.status = 'FAILURE'
                task.traceback = traceback_msg
                task.end_time = timezone.now()
                task.save()
                return server

            subnet_info_list = vqip_instance_List.list_subnets(
                server, element, uf, task_id)
            print("############### List of SUBNETS ###############")
            print(subnet_info_list)

            if subnet_info_list in instance_tools.retorna_excecao():
                traceback_msg = str(subnet_info_list)
                task = Task.objects.get(task_id=task_id)
                task.status = 'FAILURE'
                task.traceback = traceback_msg
                task.end_time = timezone.now()
                task.save()
                return subnet_info_list

            # Selecionando Próximo IPV4 Livre:
            vqip_instance_NextFreeIPv4 = SelectNextFreeIPv4()
            ipfixo = vqip_instance_NextFreeIPv4.Select_next_free_Ipv4(
                server, subnet_info_list, task_id, uf)
            print("############### IP FIXO ###############")
            print(ipfixo)

            if ipfixo in instance_tools.retorna_excecao():
                traceback_msg = str(ipfixo)
                task = Task.objects.get(task_id=task_id)
                task.status = 'FAILURE'
                task.traceback = traceback_msg
                task.end_time = timezone.now()
                task.save()
                return ipfixo

            # Adicionando IPV4 Selecionado:
            vqip_intance_addIPv4Selected = addIPv4Selected()
            result = vqip_intance_addIPv4Selected.add_IPv4_Selected(
                ipfixo, gponid, uf, task_id)
            print("############### Resultado ###############")
            print(result)

            if ipfixo in instance_tools.retorna_excecao():
                traceback_msg = str(ipfixo)
                task = Task.objects.get(task_id=task_id)
                task.status = 'FAILURE'
                task.traceback = traceback_msg
                task.end_time = timezone.now()
                task.save()
                return ipfixo

    except SoftTimeLimitExceeded:
        task = Task.objects.get(task_id=task_id)
        task.status = 'FAILURE'
        task.end_time = timezone.now()
        task.save()

    except Exception as e:
        traceback_msg = str(e)
        task = Task.objects.get(task_id=task_id)
        task.status = 'FAILURE'
        task.traceback = traceback_msg
        task.end_time = timezone.now()
        task.save()

        return {'message': traceback_msg, 'status': task.status}

    try:
        with transaction.atomic():
            task = Task.objects.get(task_id=task_id)
            # IPv6 block by Name and poolName | Pesquisa de Bloco
            ErrorsKey_instance = errorKeyExcptions()
            block_by_name_instance = ipv6BlockByName()
            poolName_WAN = "POOL TESTE FTTOFFICE WAN"
            poolName_LAN = "POOL TESTE FTTOFFICE LAN"
            BlockByName_response_wan = block_by_name_instance.ipv6_block_by_name(
                server, element, uf, poolName_WAN)

            error_response = ErrorsKey_instance.handle_error(
                BlockByName_response_wan)

            if error_response:
                print('caindo aqui')
                print(error_response)
                print("Fazendo roolback para IPv4")
                instance_delete_ipv4 = DeleteIPv4Addr()
                # Chama a função de roolback para IPv4
                instance_delete_ipv4.delete_IPv4(task.gponid, uf, task_id)
                task.ipv4 = None
                task.subnet = None
                task.subnetMask = None
                task.status = 'FAILURE'
                task.traceback = error_response['errorKey']
                task.save()
                return error_response

            print("############### IPv6 block by Name and poolName LAN ###############")
            print(BlockByName_response_wan)

            BlockByName_response_lan = block_by_name_instance.ipv6_block_by_name(
                element, uf, poolName_LAN)

            error_response = ErrorsKey_instance.handle_error(
                BlockByName_response_lan)

            if error_response:
                # Chama a função de roolback para IPv4
                instance_delete_ipv4 = DeleteIPv4Addr()
                print("Fazendo roolback para IPv4")
                instance_delete_ipv4.delete_IPv4(task.gponid, uf, task_id)
                task.ipv4 = None
                task.subnet = None
                task.subnetMask = None
                task.status = 'FAILURE'
                task.traceback = error_response['errorKey']
                task.save()
                return error_response

            print("############### IPv6 block by Name and poolName LAN ###############")
            print(BlockByName_response_lan)

            # add IPv6Subnet ALGORITHM | Informações do bloco

            # CHAMADA WAN
            addI_ipv6_subnet_instance = add_IPv6_Subnet()
            add_subnet_wan = addI_ipv6_subnet_instance.add_IPv6_Subnet(server,
                                                                       element=BlockByName_response_wan['poolName'],
                                                                       parentPool=BlockByName_response_wan['parentPool'],
                                                                       blockAddress=BlockByName_response_wan['address'],
                                                                       subnetPrefixLength='64',
                                                                       uf=uf,
                                                                       prefixLength=BlockByName_response_wan['prefixLength'])

            print("############### add IPv6Subnet ALGORITHM ###############")
            print(f'WAN: {add_subnet_wan}')

            error_response = ErrorsKey_instance.handle_error(add_subnet_wan)

            if error_response:
                # Chama a função de roolback para IPv4
                print("Fazendo roolback para IPv4")
                DeleteIPv4Addr.delete_IPv4(task.gponid, uf, task_id)
                task.status = 'FAILURE'
                task.traceback = error_response['errorKey']
                task.ipv4 = None
                task.subnet = None
                task.subnetMask = None
                task.save()
                return error_response

            # CHAMADA LAN
            add_subnet_lan = addI_ipv6_subnet_instance.add_IPv6_Subnet(server,
                                                                       element=BlockByName_response_lan['poolName'],
                                                                       parentPool=BlockByName_response_lan['parentPool'],
                                                                       blockAddress=BlockByName_response_lan['address'],
                                                                       subnetPrefixLength='56',
                                                                       uf=uf,
                                                                       prefixLength=BlockByName_response_lan['prefixLength'])

            print(f'LAN: {add_subnet_lan }')

            error_response = ErrorsKey_instance.handle_error(add_subnet_lan)

            if error_response:
                # Chama a função de roolback para IPv4
                print("Fazendo roolback para IPv4")
                DeleteIPv4Addr.delete_IPv4(task.gponid, uf, task_id)
                task.ipv4 = None
                task.subnet = None
                task.subnetMask = None
                task.status = 'FAILURE'
                task.traceback = error_response['errorKey']
                task.save()
                return error_response

            instance_Tools = Tools()
            address_ipv6_WAN = instance_Tools.extrair_endereco_ipv6(
                add_subnet_wan)
            address_ipv6_LAN = instance_Tools.extrair_endereco_ipv6(
                add_subnet_lan)

            task = Task.objects.get(task_id=task_id)
            task.ipv6_wan = address_ipv6_WAN
            task.ipv6_lan = address_ipv6_LAN

            print(f'WAN: {address_ipv6_WAN}')
            print(f'LAN: {address_ipv6_LAN}')

            # MODIFY V6 SUBNET | Altera Nome e endereço da Subnet Alocada
            gponid_wan = gponid + '_WAN'
            gponid_lan = gponid + '_LAN'
            ModifyV6Subnet_instance = ModifyV6Subnet()

            change_name_WAN = ModifyV6Subnet_instance.Modify_V6_Subnet(server, 
                                                                       gponid_wan, 
                                                                       address_ipv6_WAN, 
                                                                       uf, element, 
                                                                       '64', 
                                                                       poolName_WAN)

            task.gponid_wan = gponid_wan
            task.gponid_lan = gponid_lan
            task.save()

            print("############### MODIFY V6 SUBNET ###############")
            error_response = ErrorsKey_instance.handle_error(change_name_WAN)

            if error_response:
                # Chama a função de roolback para IPv4
                print("Fazendo roolback para IPv4")
                DeleteIPv4Addr.delete_IPv4(server, task.gponid, uf, task_id)
                task.ipv4 = None
                task.subnet = None
                task.subnetMask = None
                task.status = 'FAILURE'
                task.traceback = error_response['errorKey']
                task.save()
                return error_response

            change_name_LAN = ModifyV6Subnet_instance.Modify_V6_Subnet(server,
                                                                       gponid_lan, 
                                                                       address_ipv6_LAN, 
                                                                       uf, 
                                                                       element, 
                                                                       '56', 
                                                                       poolName_LAN)

            error_response = ErrorsKey_instance.handle_error(change_name_LAN)

            if error_response:
                # Chama a função de roolback para IPv4
                print("Fazendo roolback para IPv4")
                DeleteIPv4Addr.delete_IPv4(task.gponid, uf, task_id)
                task.ipv4 = None
                task.subnet = None
                task.subnetMask = None
                task.status = 'FAILURE'
                task.traceback = error_response['errorKey']
                task.save()
                return error_response

            if change_name_WAN == 'SUCCESS' and change_name_LAN == 'SUCCESS':
                print(f'WAN: {change_name_WAN}')
                print(f'LAN: {change_name_LAN}')

            else:
                print("else")
                print(f'WAN: {change_name_WAN}')
                print(f'LAN: {change_name_LAN}')

            if task.ipv4 is None:
                instance_delete_ipv6 = DeleteIPv6Subnet()
                instance_delete_ipv6.Delete_IPv6_Subnet(
                    task.gponid+'_WAN', uf, '64')
                instance_delete_ipv6.Delete_IPv6_Subnet(
                    task.gponid+'_LAN', uf, '56')
                task.ipv6_wan = None
                task.ipv6_lan = None
                task.status = 'FAILURE'
                task.save()

    except Exception as e:
        traceback_msg = str(e)
        task = Task.objects.get(task_id=task_id)
        task.status = 'FAILURE'
        task.traceback = traceback_msg
        task.end_time = timezone.now()
        task.save()

        return {'message': traceback_msg, 'status': task.status}

    task = Task.objects.get(task_id=task_id)
    return {'message': 'Cadastro do GPONID e IPV4 realizado com sucesso.', 'status': task.status}
