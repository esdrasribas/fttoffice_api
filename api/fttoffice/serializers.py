from rest_framework import serializers

class CadastroIpv4Serializer(serializers.Serializer):
    elemento = serializers.CharField()
    gponid = serializers.CharField()


class ConsultaIpv4Serializer(serializers.Serializer):
    gponid = serializers.CharField()


class DeleteIpv4Serializer(serializers.Serializer):
    ipv4 = serializers.CharField()