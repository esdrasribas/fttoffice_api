from rest_framework import serializers
from django.core.validators import RegexValidator


class CadastrarAprovisionamentoSerializer(serializers.Serializer):
    elemento = serializers.CharField()
    gponid = serializers.CharField()
    uf = serializers.CharField(
            validators=[
                RegexValidator(
                regex='^[A-Za-z]{2}$',
                message='O campo UF deve ter exatamente 2 letras.'
            )
        ]
    )

class CadastroIpv6Serializer(serializers.Serializer):
    elemento = serializers.CharField()
    gponid = serializers.CharField()
    uf = serializers.CharField(
            validators=[
                RegexValidator(
                regex='^[A-Za-z]{2}$',
                message='O campo UF deve ter exatamente 2 letras.'
            )
        ]
    )


class ConsultaSerializer(serializers.Serializer):
    gponid = serializers.CharField()
    uf = serializers.CharField(
            validators=[
                RegexValidator(
                regex='^[A-Za-z]{2}$',
                message='O campo UF deve ter exatamente 2 letras.'
            )
        ]
    )



class DeleteSerializer(serializers.Serializer):
    gponid = serializers.CharField()
    uf = serializers.CharField(
            validators=[
                RegexValidator(
                regex='^[A-Za-z]{2}$',
                message='O campo UF deve ter exatamente 2 letras.'
            )
        ]
    )



class TaskResultSerializer(serializers.Serializer):
    ipv4 = serializers.CharField()
    gponid = serializers.CharField()


class ConsultarTarefasSerializer(serializers.Serializer):
    task_id = serializers.UUIDField()

