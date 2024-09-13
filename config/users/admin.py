from django.contrib import admin
from .models import User

class TempUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'nickname', 'is_active', 'is_admin')
    search_fields = ('email', 'nickname')
    list_filter = ('is_active', 'is_admin')

admin.site.register(User, TempUserAdmin)