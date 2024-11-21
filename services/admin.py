from django.contrib import admin
from .models import Coupon, Service, StaffService
from unfold.admin import ModelAdmin


@admin.register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = ('coupon_code', 'discount', 'valid_from', 'valid_until', 'created_at')
    list_filter = ('valid_from', 'valid_until')
    search_fields = ('coupon_code',)


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = ('service_name', 'duration', 'price', 'applied_coupon_code')
    list_filter = ('coupon',)  # Corrected to be a tuple    search_fields = ('service_name', 'description')

    def get_readonly_fields(self, request, obj=None):
        return ('applied_coupon_code',)


@admin.register(StaffService)
class StaffServiceAdmin(ModelAdmin):
    list_display = ('staff', 'service', 'is_primary')
    list_filter = ('is_primary',)
