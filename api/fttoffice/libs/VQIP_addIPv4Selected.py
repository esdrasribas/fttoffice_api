from bs4 import BeautifulSoup
import requests


class addIPv4Selected:
    def add_IPv4_Selected(self, ip_fixo, GPONID):
        try:
            url = "http://10.61.184.101:8080/ws/services/VQIPWebService/"
            headers = {
                'Content-Type': 'text/xml; charset=utf-8'
            }
            response = requests.request('POST',
                                        url,
                                        headers=headers,
                                        data=self.xml_VQIP_addIPv4Selected(
                                            ip_fixo, GPONID),
                                        timeout=30)

            soup = BeautifulSoup(response.content, 'xml')
            result_element = soup.find('ns1:result')

            if result_element and result_element.text != 'SUCCESS':
                message = f"Falha na chamada da API: {result_element.text}"
                print(message)
                return message

            else:
                print(result_element.text)
                return result_element.text


        except Exception as e:
            print(f"Falha na chamada da API: {e}")


    def xml_VQIP_addIPv4Selected(self, ip_fixo, GPONID):
        user = "vt38823"
        senha = "abcd12345"
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" soapenv:mustUnderstand="1">
                    <wsse:UsernameToken wsu:Id="UsernameToken-CD5DFBCF2AAC93CF1116899413896331">
                        <wsse:Username>{user}</wsse:Username>
                        <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{senha}</wsse:Password>
                    </wsse:UsernameToken>
                </wsse:Security>
                <wsa:To>http://10.61.184.101:8080/ws/services/VQIPWebService</wsa:To>
                <wsa:MessageID>urn:uuid:e9ae745e-029c-4f88-94c5-6e5a26b8d7f0</wsa:MessageID>
                <wsa:Action>VQIPManager_AddRequest</wsa:Action>
            </soapenv:Header>
            <soapenv:Body>
                <ns1:AddRequest xmlns:ns1="http://alcatel-lucent.com/qip/nb/ws">
                    <ns1:commonParam>
                        <ns1:organization>OI_Regiao_1</ns1:organization>
                        <ns1:locale>pt_BR</ns1:locale>
                    </ns1:commonParam>
                    <ns1:reqObject xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="ns1:V4_ADDR_REC">
                        <ns1:objectAddr>{ip_fixo}</ns1:objectAddr>
                        <ns1:objectName>{GPONID}</ns1:objectName>
                        <ns1:isAddSelected>true</ns1:isAddSelected>
                    </ns1:reqObject>
                </ns1:AddRequest>
            </soapenv:Body>
        </soapenv:Envelope>"""