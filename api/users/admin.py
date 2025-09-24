from django.contrib import admin
from users.models import Role, User, AuthProvider, UserAuthProvider


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "is_active", "is_staff", "date_joined")
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_active", "is_staff", "roles__name")
    filter_horizontal = ("roles",)


@admin.register(AuthProvider)
class AuthProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(UserAuthProvider)
class UserAuthProviderAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "is_primary",)
    search_fields = ("user__email", "provider__name", "provider_user_id")
    list_filter = ("is_primary", "provider__name")
    raw_id_fields = ("user", "provider")
