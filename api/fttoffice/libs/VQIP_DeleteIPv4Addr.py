from bs4 import BeautifulSoup
import requests
from fttoffice.libs.exceptError import V4ObjectNotFoundError

class DeleteIPv4Addr:
    def delete_IPv4(self, ipv4):
        try:
            url = "http://10.61.184.101:8080/ws/services/VQIPWebService/"
            headers = {
                'Content-Type': 'text/xml; charset=utf-8'
            }
            response = requests.request('POST',
                                        url,
                                        headers=headers,
                                        data=self.xml_VQIP_DeleteIPv4Addr(
                                            ipv4),
                                        timeout=30)
            soup = BeautifulSoup(response.content, 'xml')
            result_element = soup.find('ns1:result')

            if result_element and result_element.text != 'SUCCESS':
                result_error = soup.find('ns1:errorKey')
                return result_error.text

            else:
                print(result_element.text)
                return f'IPv4 Deletado com sucesso.'
            
        except V4ObjectNotFoundError as e:
            print(f"Endereço de IPv4 não existe: {e}")
            return "Endereço de IPv4 não existe."
        
        except Exception as e:
            print(f"Falha na chamada da api: {e}")
            return f"Falha na chamada da api: {e}"
            

    def xml_VQIP_DeleteIPv4Addr(self, ipv4):
        user = "vt38823"
        senha = "abcd12345"
        return f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
        <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
            <wsse:Security soapenv:mustUnderstand="1" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
                <wsse:UsernameToken wsu:Id="UsernameToken-DBCC17DED37E8E2CF216899368847461">
                    <wsse:Username>{user}</wsse:Username>
                    <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{senha}</wsse:Password>
                </wsse:UsernameToken>
            </wsse:Security>
            <wsa:To>http://10.61.184.101:8080/ws/services/VQIPWebService</wsa:To>
            <wsa:MessageID>urn:uuid:284e2892-9d3a-4d5b-ae4f-26c74e53c82a</wsa:MessageID>
            <wsa:Action>VQIPManager_DeleteRequest</wsa:Action>
        </soapenv:Header>
        <soapenv:Body>
            <ns1:DeleteRequest xmlns:ns1="http://alcatel-lucent.com/qip/nb/ws">
                <ns1:commonParam>
                    <ns1:organization>OI_Regiao_1</ns1:organization>
                    <ns1:locale>pt_BR</ns1:locale>
                </ns1:commonParam>
                <ns1:reqObject xsi:type="ns1:V4_ADDR_REC" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                    <ns1:objectAddr>{ipv4}</ns1:objectAddr>
                </ns1:reqObject>
            </ns1:DeleteRequest>
        </soapenv:Body>
        </soapenv:Envelope>"""
    
# vqip_instance = delete_IPv4()
# ipv4Dell = vqip_instance.deleteIPv4('189.49.208.3')