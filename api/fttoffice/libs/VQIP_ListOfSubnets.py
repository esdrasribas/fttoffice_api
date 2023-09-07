from bs4 import BeautifulSoup
import requests

class ListOfSubnets:
    def list_subnets(self, element):
        try:
            url = "http://10.61.184.101:8080/ws/services/VQIPWebService/"
            headers = {
                'Content-Type': 'text/xml; charset=utf-8'
            }
            response = requests.request('POST',
                                        url,
                                        headers=headers,
                                        data=self.xml_VQIP_ListOfSubnets(
                                            element),
                                        timeout=30)

            subnetAddress_list = []
            soup = BeautifulSoup(response.content, 'xml')
            result_element = soup.find('ns1:result')

            if result_element and result_element.text != 'SUCCESS':
                message = f"Falha na chamada da API: {result_element.text}"
                print(message)
                return message
            else:
                subnet_elements = soup.find_all('ns1:subnetAddress')
                for subnet_element in subnet_elements:
                    subnetAddress_list.append(subnet_element.text)
                return subnetAddress_list

        except Exception as e:
            print(f"Falha na chamada da API: {e}")

    def xml_VQIP_ListOfSubnets(self, element):
        user = "vt38823"
        senha = "abcd12345"
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" soapenv:mustUnderstand="1">
                    <wsse:UsernameToken wsu:Id="UsernameToken-151886493872F148B116897782107381">
                        <wsse:Username>{user}</wsse:Username>
                        <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{senha}</wsse:Password>
                    </wsse:UsernameToken>
                </wsse:Security>
                <wsa:To>http://10.81.125.27:8080/ws/services/VQIPWebService</wsa:To>
                <wsa:MessageID>urn:uuid:ec8a6bfb-f380-495e-bb6a-28dd0b981e9d</wsa:MessageID>
                <wsa:Action>VQIPManager_PageSearchRequest</wsa:Action>
            </soapenv:Header>
            <soapenv:Body>
                <ns1:PageSearchRequest xmlns:ns1="http://alcatel-lucent.com/qip/nb/ws">
                    <ns1:commonParam>
                        <ns1:organization>OI_Regiao_1</ns1:organization>
                        <ns1:locale>pt_BR</ns1:locale>
                    </ns1:commonParam>
                    <ns1:reqObject xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="ns1:SEARCH_V4_SUBNET_REC">
                        <ns1:name>{element}</ns1:name>
                        <ns1:domain>user3p.vtal.net.br</ns1:domain>
                    </ns1:reqObject>
                    <ns1:pageCount>1</ns1:pageCount>
                    <ns1:pageSize>0</ns1:pageSize>
                </ns1:PageSearchRequest>
            </soapenv:Body>
        </soapenv:Envelope>"""
    

# Chame o método list_subnets da instância
# vqip_instance = ListOfSubnets()
# subnets = vqip_instance.list_subnets("CON-MG-SER-A01")
# print(subnets)
