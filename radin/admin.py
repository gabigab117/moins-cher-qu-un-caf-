from django.contrib import admin
from .models import Confession


@admin.register(Confession)
class ConfessionAdmin(admin.ModelAdmin):
    list_display = ['body', 'created_at', 'votes_genie', 'votes_rat']
    list_filter = ['created_at']
    search_fields = ['body']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

