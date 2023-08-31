from django.contrib import admin
from .models import Elevator

@admin.register(Elevator)
class ElevatorAdmin(admin.ModelAdmin):
    list_display = ['id', 'current_floor', 'status', 'direction', 'door']
    actions = ['mark_maintenance']

    def mark_maintenance(self, request, queryset):
        queryset.update(status='NW')
