from django.contrib import admin

from .models import Overlay


@admin.register(Overlay)
class OverlayAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'url_name', 'current')
    list_display = ('user', 'site', 'url_name', 'current')
    list_filter = ('url_name', 'current')
