from django.contrib import admin
from .models import Coupon, Service, StaffService
from unfold.admin import ModelAdmin
from django.utils.html import format_html


@admin.register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = (
        "id",
        "coupon_code",
        "discount",
        "valid_from",
        "valid_until",
        "created_at",
    )  # Added 'id'
    list_filter = ("valid_from", "valid_until")
    search_fields = ("coupon_code",)


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = (
        "id",
        "service_name",
        "duration",
        "coupon",
        "price",
        "image_preview",
    )  # Added 'id'
    list_filter = ("coupon", "price")
    search_fields = ("service_name", "description")

    def image_preview(self, obj):
        if obj.service_image:
            return format_html(
                '<img src="{}" width="50" height="50" />', obj.service_image.url
            )
        return "No Image"

    image_preview.short_description = "Image"


@admin.register(StaffService)
class StaffServiceAdmin(ModelAdmin):
    list_display = (
        "id",
        "staff",
        "service",
        "is_primary",
        "date",
        "start_time",
        "end_time",
        "status",
    )
    list_filter = ("is_primary", "status")
