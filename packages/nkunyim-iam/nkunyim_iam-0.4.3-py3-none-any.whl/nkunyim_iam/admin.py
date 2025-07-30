from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UAdmin
from django.utils.translation import gettext_lazy as _
from nkunyim_iam.models import User


class UserAdmin(UAdmin):
    fieldsets = (
        (_('Account'), {
            'fields': (
                'email_address',
                'password',
            )
        }),
        (_('Profile'), {
            'fields': (
                'phone_number',
                'nickname',
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_admin',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'nickname',
                'phone_number',
                'email_address',
                'password1',
                'password2',
            ),
        }),
    )
    list_display = ('username', 'nickname', 'phone_number', 'email_address', 'is_staff',)
    list_filter = ('is_superuser', 'is_active', 'groups',)
    search_fields = ('username', 'nickname', 'phone_number', 'email_address')
    ordering = ('nickname', 'email_address',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(User, UserAdmin)
