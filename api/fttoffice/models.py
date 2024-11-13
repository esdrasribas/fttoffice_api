from django.db import models
import uuid

class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    elemento = models.CharField(max_length=255, help_text="Nome do elemento")
    gponid = models.CharField(max_length=255, help_text="GPONID")
    uf = models.CharField(max_length=2, null=True)
    task_id = models.UUIDField(unique=True, help_text="ID da tarefa", editable=False)
    start_time = models.DateTimeField(auto_now_add=True, help_text="Data e hora de início")
    end_time = models.DateTimeField(null=True, blank=True, help_text="Data e hora de conclusão")
    traceback = models.TextField(null=True, blank=True, help_text="Rastreamento da exceção")
    request_time = models.DateTimeField(auto_now=True, help_text="Data e hora da solicitação")
    status = models.CharField(max_length=255, default="PENDING")
    ipv4 = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True, help_text="Endereço IPv4")
    subnet = models.CharField(max_length=255, blank=True, null=True, help_text="Subnet")
    data_delecao = models.DateTimeField(null=True, blank=True)
    subnetMask = models.CharField(max_length=15, null=True, blank=True, help_text="SubnetMask")
    details = models.CharField(max_length=255, null=True, blank=True, help_text="Rastreamento de deleção VITAL QIP")
    ipv6_wan = models.GenericIPAddressField(protocol='IPv6', null=True, blank=True, help_text="Endereço IPv6 WAN")
    ipv6_lan = models.GenericIPAddressField(protocol='IPv6', null=True, blank=True, help_text="Endereço IPv6 LAN")
    gponid_wan = models.CharField(max_length=255, help_text="GPONID WAN", default='')
    gponid_lan = models.CharField(max_length=255, help_text="GPONID LAN", default='')
    
    def __str__(self):
        return f'{self.task_id}'

