from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Appointment, Payment
from accounts.models import Role, User
from services.models import Service

from django.utils.html import format_html
# Register your models here.


@admin.register(Appointment)
class CustomAppointmentClass(ModelAdmin):
    list_display = [
        "id",
        "user_email",
        "staff_email",
        "formatted_appointment_time",
        "status",
        "total_services",
        "total_price",
        "coupon_details",
    ]

    # Filtering options
    list_filter = ["status", "appointment_time", "created_at"]

    # Search functionality
    search_fields = ["user__email", "staff__email", "services__service_name"]

    # Readonly fields for calculated values
    readonly_fields = ["created_at", "display_price_breakdown", "coupon_details"]

    # Custom methods for display
    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "Customer"

    def staff_email(self, obj):
        return obj.staff.email

    staff_email.short_description = "Staff"

    def formatted_appointment_time(self, obj):
        return obj.appointment_time.strftime("%Y-%m-%d %H:%M")

    formatted_appointment_time.short_description = "Appointment Time"

    def total_services(self, obj):
        return obj.services.count()

    total_services.short_description = "Services"

    def total_price(self, obj):
        return f"${obj.calculate_total_price():.2f}"

    total_price.short_description = "Total Price"

    def display_price_breakdown(self, obj):
        breakdown = obj.get_price_breakdown()
        html = "<table>"
        html += "<tr><th>Service</th><th>Price</th><th>Discount</th></tr>"
        for service in breakdown["services"]:
            html += f"<tr><td>{service['name']}</td><td>${service['price']:.2f}</td><td>${service['discount']:.2f}</td></tr>"
        html += f"<tr><th>Total</th><td>${breakdown['base_total']:.2f}</td><td>${breakdown['total_discount']:.2f}</td></tr>"
        html += f"<tr><th>Final Total</th><td colspan='2'>${breakdown['final_total']:.2f}</td></tr>"
        html += "</table>"
        return format_html(html)

    display_price_breakdown.short_description = "Price Breakdown"
    filter_horizontal = ("services",)

    def coupon_status(self, obj):
        coupon_codes = obj.get_applied_coupon_codes()
        return f"Coupons: {', '.join(coupon_codes) if coupon_codes else 'No coupons'}"

    # Optional: Add coupon selection if your model supports it
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "services":
            # Optionally add custom queryset filtering for services
            kwargs["queryset"] = Service.objects.all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # If you want to show coupon information
    def get_readonly_fields(self, request, obj=None):
        # Existing readonly fields
        readonly = list(self.readonly_fields)

        # Optionally add coupon-related fields if needed
        # readonly.append('coupon_details')

        return readonly

    def coupon_details(self, obj):
        # Example method to show coupon details if applicable
        # This depends on how coupons are associated with your model
        services = obj.services.all()
        coupons = set(service.coupon for service in services if service.coupon)

        if coupons:
            return ", ".join(str(coupon) for coupon in coupons)
        return "No coupons applied"

    coupon_details.short_description = "Applied Coupons"


@admin.register(Payment)
class CustomPaymentClass(ModelAdmin):
    list_display = (
        "appointment",
        "user",
        "amount",
        "payment_method",
        "payment_status",
        "transaction_date",
    )
    list_filter = ("payment_status", "payment_method")
    search_fields = ("appointment__user__email", "user__email", "payment_method")

    def get_queryset(self, request):
        """Customize Payment admin panel to show only relevant payment records"""
        queryset = super().get_queryset(request)
        # Example: you can filter payments by status or other criteria
        # queryset = queryset.filter(payment_status='completed')
        return queryset
