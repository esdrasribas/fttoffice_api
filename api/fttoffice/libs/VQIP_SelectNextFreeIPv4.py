from bs4 import BeautifulSoup
import random
import requests

class SelectNextFreeIPv4:
    def __init__(self):
        self.used_subnets = set()

    def Select_next_free_Ipv4(self, subnetsAddress):
        url = "http://10.61.184.101:8080/ws/services/VQIPWebService/"
        headers = {
            'Content-Type': 'text/xml; charset=utf-8'
        }
        subnet = self.get_subnet(subnetsAddress)


        if subnet is None:
            print('Não há mais subnets disponíveis listado pelo endpoint "List_Of_Subnets"')
            return None
        
        response = requests.request('POST',
                                    url,
                                    headers=headers,
                                    data=self.xml_VQIP_SelectNextFreeIPv4(
                                        "OI_Regiao_1", subnet),
                                    timeout=30)
        
        soup = BeautifulSoup(response.content, 'xml')
        result_element = soup.find('ns1:result')
        ipfixo_element = soup.find('ns1:ipAddrStr')
        ipfixo = ipfixo_element.text.strip()

        if result_element and result_element.text != 'SUCCESS':
            return None
        else:
            if self.valida_ip(ipfixo):
                return ipfixo
            else:
                print("IP fixo inválido, tentando novamente...")
                return self.Select_next_free_Ipv4(subnetsAddress)

    def xml_VQIP_SelectNextFreeIPv4(self, regiao, subnet):
        user = "vt38823"
        senha = "abcd12345"
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" soapenv:mustUnderstand="1">
                    <wsse:UsernameToken wsu:Id="UsernameToken-98D8528C560188618E16899328142511">
                        <wsse:Username>{user}</wsse:Username>
                        <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{senha}</wsse:Password>
                    </wsse:UsernameToken>
                </wsse:Security>
                <wsa:To>http://10.61.184.101:8080/ws/services/VQIPWebService</wsa:To>
                <wsa:MessageID>urn:uuid:446c8c0e-eb51-4c99-8ed6-6cba91d5ea0c</wsa:MessageID>
                <wsa:Action>VQIPManager_GetRequest</wsa:Action>
            </soapenv:Header>
            <soapenv:Body>
                <ns1:GetRequest xmlns:ns1="http://alcatel-lucent.com/qip/nb/ws">
                    <ns1:commonParam>
                        <ns1:organization>{regiao}</ns1:organization>
                        <ns1:locale>pt_BR</ns1:locale>
                    </ns1:commonParam>
                    <ns1:reqObject xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="ns1:V4_GET_IP_ADDRESS_REC">
                        <ns1:ipAddrStr>{subnet}</ns1:ipAddrStr>
                    </ns1:reqObject>
                </ns1:GetRequest>
            </soapenv:Body>
        </soapenv:Envelope>"""

    def valida_ip(self, ip):
        if ip is None:
            return False
        
        partes = ip.split(".")
        ultimo_octeto = partes[-1]

        if ultimo_octeto != "0":
            return True
        else:
            return False

    def get_subnet(self, subnetsAddressList):

        available_subnets = [
            subnet for subnet in subnetsAddressList if subnet not in self.used_subnets]

        if not available_subnets:
            print("Não há mais subnets disponíveis.")
            return None

        subnet = random.choice(available_subnets)
        self.used_subnets.add(subnet)
        print(f"Subnet escolhida: {subnet}")
        return subnet




# vqip_instance = SelectNextFreeIPv4()
# listsubnets = vqip_instance.Select_next_free_Ipv4(['152.238.200.0', '179.199.212.0', '186.241.118.0'])

