from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'role', 'first_name', 'last_name')
    list_display_links = ('id', 'username',)
    search_fields = ('username', 'first_name', 'last_name')
    list_filter = ('role',)
