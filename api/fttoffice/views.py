from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import CadastroIpv4Serializer
from .serializers import ConsultaIpv4Serializer
from .serializers import DeleteIpv4Serializer
from fttoffice.libs.VQIP_ListOfSubnets import ListOfSubnets
from fttoffice.libs.VQIP_SelectNextFreeIPv4 import SelectNextFreeIPv4
from fttoffice.libs.VQIP_addIPv4Selected import addIPv4Selected
from fttoffice.libs.VQIP_RetrieveIPv4address import RetrieveIPv4address
from fttoffice.libs.VQIP_DeleteIPv4Addr import DeleteIPv4Addr
from fttoffice.libs.exceptError import WS_OBJECT_NAME_NOT_FOUND


class CadastrarAprovisionamentoIPv4View(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CadastroIpv4Serializer(data=request.data)

        if serializer.is_valid():
            element = serializer.validated_data['elemento']
            gponid = serializer.validated_data['gponid']

            # Listando subnets:
            vqip_instance_List = ListOfSubnets()
            subnets = vqip_instance_List.list_subnets(element=element)
            print("############### List of SUBNETS ###############")
            print(subnets)

            # Selecionando Próximo IPV4 Livre:
            vqip_instance_NextFreeIPv4 = SelectNextFreeIPv4()
            ipfixo = vqip_instance_NextFreeIPv4.Select_next_free_Ipv4(subnets)
            print("############### IP FIXO ###############")
            print(ipfixo)

            # Adicionando IPV4 Selecionado:
            vqip_intance_addIPv4Selected = addIPv4Selected()
            result = vqip_intance_addIPv4Selected.add_IPv4_Selected(ipfixo, gponid)
            print("############### Resultado ###############")
            print(result)

            return Response({'message': 'Cadastro do GPONID e IPV4 realizado com sucesso.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConsultarAprovisionamentoIPv4View(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ConsultaIpv4Serializer(data=request.data)

        if serializer.is_valid():
            gponid = serializer.validated_data['gponid']

            vqip_instance_consulta = RetrieveIPv4address()
            try:
                Retrieve = vqip_instance_consulta.Retrieve_IPv4_address(gponid)
                if Retrieve == 'WS_OBJECT_NAME_NOT_FOUND':
                    return Retrieve

                print(Retrieve)
                response = {
                    'ipv4': Retrieve['ipv4'],
                    'gponid': Retrieve['gponid']
                }
                return Response(response, status=status.HTTP_200_OK)
            
            except WS_OBJECT_NAME_NOT_FOUND as e:
                return Response({'detail': f'Endereço de IPv4 não existe: {e}'}, status=status.HTTP_404_NOT_FOUND)
            
            except Exception as e:
                return Response({'detail': f'Falha na chamada da API: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeletarAprovisionamentoIPv4View(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request):
        serializer = DeleteIpv4Serializer(data=request.data)

        if serializer.is_valid():
            ipv4 = serializer.validated_data['ipv4']
        
            vqip_intance_delete = DeleteIPv4Addr()
            response = vqip_intance_delete.delete_IPv4(ipv4)

            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
 