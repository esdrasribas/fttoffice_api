from rest_framework import status
from rest_framework.response import Response

class V4ObjectNotFoundError(Exception):
    pass

class WS_OBJECT_NAME_NOT_FOUND(Exception):
    pass


from rest_framework import status
from rest_framework.response import Response

class errorKeyExcptions:
    @staticmethod
    def handle_error(error_response):
        if error_response == 'WS_BLOCK_NOT_FOUND':
            return {'details': 'O Elemento passado não possui bloco criado.', 'errorKey': 'WS_BLOCK_NOT_FOUND'}
        elif error_response == 'WS_SUBNET_NOT_FOUND':
            return {'details': 'Subnet não encontrado.', 'errorKey': 'WS_SUBNET_NOT_FOUND'}
        elif error_response == 'IP_INVALID_V6_ADDRESS':
            return {'details': 'Endereço inválido para o bloco IPv6.', 'errorKey': 'IP_INVALID_V6_ADDRESS'}
        elif error_response == 'IPV4_INVALID_ADDRESS':
            return {'details': 'Endereço de subnet inválido.', 'errorKey': 'IPV4_INVALID_ADDRESS'}
        elif error_response == 'IPV4_OBJECT_NOT_FOUND':
            return {'details': 'Subnet não possui IPV4 disponíveis.', 'errorKey': 'IPV4_OBJECT_NOT_FOUND'}
        elif error_response == 'CLI_INVALID_IPV4_ADDRESS':
            return {'details': 'Endereço inválido para o objeto IPv4.', 'errorKey': 'CLI_INVALID_IPV4_ADDRESS'}
        elif error_response == 'GUI_IPV4_ADD_FAILED':
            return {'details': ' Endereço de objeto IPv4 já alocado', 'errorKey': 'GUI_IPV4_ADD_FAILED'}
        elif error_response == 'ELEMENT_SUBNET_DOES_NOT_EXIST':
            return {'details': 'Não existe subnet para o Elemento e UF enviada.', 'errorKey': 'ELEMENT_SUBNET_DOES_NOT_EXIST'}
        elif error_response == 'OBJECTS_EXIST_DUPLICATE_NAME':
            return {'details': 'Ja existe aprovisionamento para os parametros passados.', 'errorKey': 'OBJECTS_EXIST_DUPLICATE_NAME'}
        elif error_response == 'V4_OBJECT_NOT_FOUND_BY_ADDRESS':
            return {'details': 'Endereço IPv4 inexistente ou já tenha sido desalocado.', 'errorKey': 'V4_OBJECT_NOT_FOUND_BY_ADDRESS'}
        elif error_response == 'WS_OBJECT_NAME_NOT_FOUND':
            return {'detail':'Nome de objeto IPv4 inexistente no Vital QIP.', 'errorKey': 'WS_OBJECT_NAME_NOT_FOUND'}
        elif error_response == 'WS_SUBNET_NOT_UNIQUE':
            return {'detail':'Subnet não é unica. Só é permitido o aprovisionamento de 1 subnet para cada GPONID.', 'errorKey': 'WS_SUBNET_NOT_UNIQUE'}
        elif error_response == 'NoServersAvailable':
            return {'detais': 'Servidores VitalQIP disponível', 'erroKey': 'NoServersAvailable'}
        elif error_response == 'UNKNOWN_ERROR':
            return {'detail':'Error Desconhecido.', 'errorKey': 'UNKNOWN_ERROR'}       

        else:   
            return None
        
    @staticmethod
    def handle_error_delete(error_response):
        if error_response == 'WS_SUBNET_NOT_FOUND':
            return {'details': 'Subnet não encontrado.', 'errorKey': 'WS_SUBNET_NOT_FOUND'}
        elif error_response == 'WS_OBJECT_NAME_NOT_FOUND':
            return {'detail':'Nome de objeto IPv4 inexistente no Vital QIP.', 'errorKey': 'WS_OBJECT_NAME_NOT_FOUND'}
        elif error_response == 'WS_SUBNET_NOT_UNIQUE':
                return {'detail':'Subnet não é unica. Só é permitido o aprovisionamento de 1 subnet para cada GPONID.', 'errorKey': 'WS_SUBNET_NOT_UNIQUE'}
        elif error_response == 'IPV4_OBJECT_NOT_FOUND':
            return {'details': 'Subnet não possui IPV4 disponíveis.', 'errorKey': 'IPV4_OBJECT_NOT_FOUND'}
        else:
            return error_response
        
