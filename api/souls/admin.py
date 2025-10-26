from django.contrib import admin

from souls.models import Soul, ProgressUpdate


@admin.register(Soul)
class SoulAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone_number', 'status', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone_number')
    list_filter = ('mission', 'status', 'is_personal', 'location')
    ordering = ('-created_at',)


@admin.register(ProgressUpdate)
class ProgressUpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'soul', 'update_date', 'created_at')
    search_fields = ('soul__first_name', 'soul__last_name', 'content')
    list_filter = ('update_date',)
    ordering = ('-update_date',)