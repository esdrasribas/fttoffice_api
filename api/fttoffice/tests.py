from django.test import TestCase

# Create your tests here.
def valida_ip(ip):
    partes = ip.split(".")  # Divide o IP em partes separadas pelo ponto
    ultimo_octeto = partes[-1]  # Obtém o último octeto

    if ultimo_octeto != "0":
        return True
    else:
        return False

# Exemplos de uso
ips = ["10.61.25.0", "10.61.25.14", "10.61.25.20", "10.61.25.100", "10.61.25.200"]
for ip in ips:
    if valida_ip(ip):
        print(f"{ip} é válido")
    else:
        print(f"{ip} não é válido")


