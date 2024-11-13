from bs4 import BeautifulSoup
import requests
from fttoffice.libs.exceptError import WS_OBJECT_NAME_NOT_FOUND

class RetrieveIPv4address:
    def Retrieve_IPv4_address(self, GPONID):
        try:
            url = "URL"
            headers = {
                'Content-Type': 'text/xml; charset=utf-8'
            }
            response = requests.request('POST',
                                        url,
                                        headers=headers,
                                        data=self.xml_Retrieve_IPv4_address(
                                            GPONID),
                                        timeout=30)

            soup = BeautifulSoup(response.content, 'xml')
            result_element = soup.find('ns1:result')
            ip_fixo = soup.find('ns1:objectAddr')
            gponid = soup.find('ns1:objectName')


            if result_element and result_element.text != 'SUCCESS':
                result_error = soup.find('ns1:errorKey')
                print(result_error.text)
                return result_error.text

            else:
                ip_fixo = soup.find('ns1:objectAddr')
                gponid = soup.find('ns1:objectName')

                if ip_fixo is not None and gponid is not None:
                    response = {'ipv4': ip_fixo.text.strip(),
                                'gponid': gponid.text.strip()
                                }
                    print(response)
                    return response
                else:
                    raise WS_OBJECT_NAME_NOT_FOUND("Object name not found")

        except WS_OBJECT_NAME_NOT_FOUND as e:
            print(f"Endereço de IPv4 não existe: {e}")
            return e
        
        except Exception as e:
            print(f"Falha na chamada da API: {e}")


    def xml_Retrieve_IPv4_address(self, GPONID):
        user = "XXXX"
        senha = "XXXXX"
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" soapenv:mustUnderstand="1">
                    <wsse:UsernameToken wsu:Id="UsernameToken-731DBCBC67BAA88E5D16899544749621">
                        <wsse:Username>{user}</wsse:Username>
                        <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{senha}</wsse:Password>
                    </wsse:UsernameToken>
                </wsse:Security>
                <wsa:To>URL</wsa:To>
                <wsa:MessageID>urn:uuid:fe369f95-9fa0-4800-9af4-f079456e1369</wsa:MessageID>
                <wsa:Action>VQIPManager_GetRequest</wsa:Action>
            </soapenv:Header>
            <soapenv:Body>
                <ns1:GetRequest xmlns:ns1="http://alcatel-lucent.com/qip/nb/ws">
                    <ns1:commonParam>
                        <ns1:organization></ns1:organization>
                        <ns1:locale>pt_BR</ns1:locale>
                    </ns1:commonParam>
                    <ns1:reqObject xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="ns1:V4_ADDR_REC">
                        <ns1:objectAddr></ns1:objectAddr>
                        <ns1:objectName>{GPONID}</ns1:objectName>
                    </ns1:reqObject>
                </ns1:GetRequest>
            </soapenv:Body>
        </soapenv:Envelope>"""
    

# vqip_instance = RetrieveIPv4address()
# Consulta = vqip_instance.Retrieve_IPv4_address('20-TESTEAPI')
