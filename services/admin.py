from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import StaffProfile, StaffService
from unfold.contrib.filters.admin import TextFilter, FieldTextFilter
from accounts.models import User, Role
from django.core.validators import EMPTY_VALUES
from django.utils.html import format_html


class ServiceNameFilter(TextFilter):
    title = "Service Name"
    parameter_name = "service_name"

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            return queryset.filter(service_name__icontains=self.value())
        return queryset


class StaffServiceInline(admin.TabularInline):
    model = StaffService
    extra = 1
    verbose_name = "Service"
    verbose_name_plural = "Services"


@admin.register(StaffProfile)
class StaffProfileAdmin(ModelAdmin):
    list_display = (
        "get_full_name",
        "get_email",
        "is_available",
        "get_services_count",
    )
    list_filter = ["is_available"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "bio",
    ]
    inlines = [StaffServiceInline]

    def get_search_results(self, request, queryset, search_term):
        # Call the parent implementation to get the search results
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        # Fetch the "Customer" role instance
        customer_role = Role.objects.filter(role_name="Customer").first()
        if customer_role:
            # Exclude users with the "Customer" role
            queryset = queryset.exclude(user__user_role=customer_role)
        return queryset, use_distinct

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    get_full_name.short_description = "Name"

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = "Email"

    def get_services_count(self, obj):
        count = obj.services.count()
        return format_html('<span class="badge">{}</span>', count)

    get_services_count.short_description = "Services"
