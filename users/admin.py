from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin


@admin.action(description='Send activation email if not active', )
def send_activation_email(self, request, queryset):
    for u in queryset:
        u.send_activation_email()


class CustomUserAdmin(UserAdmin):
    actions = [send_activation_email]

    fieldsets = (
        *UserAdmin.fieldsets,  # original form fieldsets, expanded
        (  # new fieldset added on to the bottom
            '',  # group heading of your choice; set to None for a blank space instead of a header
            {
                'fields': (
                    'is_email_verified',
                    'followers'
                ),
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)
