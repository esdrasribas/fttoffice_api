from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Task


@receiver(post_save, sender=Task)
def set_end_time(sender, instance, **kwargs):
    if instance.status == 'ATIVO' and not instance.end_time:
        instance.end_time = timezone.now()
        instance.save()


@receiver(post_save, sender=Task)
def update_status(sender, instance, **kwargs):
    if kwargs.get('created', False):
        return

    if instance.status == 'PENDING':
        return

    try:
        if instance.status == 'ATIVO':
            if not instance.end_time:
                instance.end_time = timezone.now()
        elif instance.status == 'FAILURE':
            if not instance.end_time:
                instance.end_time = timezone.now()

    except Exception as e:
        instance.traceback = str(e)
        instance.status = 'FAILURE'
        instance.end_time = timezone.now()

