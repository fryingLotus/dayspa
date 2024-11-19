from unfold.admin import ModelAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    # Set the forms
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ("email", "first_name", "last_name",
                    "user_role", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    # Fields for editing existing users
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "user_role")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )

    # Fields for adding new users
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "user_role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    filter_horizontal = ()


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ("role_name",)
    search_fields = ("role_name",)
    ordering = ("role_name",)
