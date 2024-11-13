from django.contrib import admin
from .models import Task

class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('start_time',)
    fields = ('elemento', 'gponid', 'uf', 'subnet','subnetMask', 'ipv4', 'gponid_wan', 'ipv6_wan', 'gponid_lan', 'ipv6_lan', 'start_time', 'end_time', 'traceback', 'status')
    list_display = ('task_id', 'elemento', 'gponid', 'status')


admin.site.register(Task, TaskAdmin)

