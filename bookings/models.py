from django.db import models
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from accounts.models import User  # Import User from the accounts app
from services.models import Service  # Import Service from the services app


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("canceled", "Canceled"),
        ("completed", "Completed"),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="client_appointments"
    )
    services = models.ManyToManyField(Service, related_name="appointments")
    staff = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="staff_appointments"
    )
    appointment_time = models.DateTimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total_price(self):
        """Calculate the total price including any applicable discounts"""
        # Get base total from all services
        base_total = self.services.aggregate(total=Sum("price"))["total"] or Decimal(
            "0"
        )

        # Calculate discounts from valid coupons
        total_discount = Decimal("0")
        current_time = timezone.now()

        for service in self.services.all():
            if (
                service.coupon
                and service.coupon.valid_from
                <= current_time
                <= service.coupon.valid_until
            ):
                # Calculate discount amount for this service
                discount_amount = (
                    service.price * service.coupon.discount / Decimal("100")
                )
                total_discount += discount_amount

        # Calculate final price
        final_price = base_total - total_discount
        return max(final_price, Decimal("0"))  # Ensure price doesn't go below 0

    def get_price_breakdown(self):
        """Get detailed breakdown of prices and discounts"""
        breakdown = {
            "services": [],
            "base_total": Decimal("0"),
            "total_discount": Decimal("0"),
            "final_total": Decimal("0"),
        }

        current_time = timezone.now()

        for service in self.services.all():
            service_detail = {
                "name": service.service_name,
                "price": service.price,
                "discount": Decimal("0"),
            }

            if (
                service.coupon
                and service.coupon.valid_from
                <= current_time
                <= service.coupon.valid_until
            ):
                service_detail["discount"] = (
                    service.price * service.coupon.discount / Decimal("100")
                )
                service_detail["coupon_code"] = service.coupon.coupon_code

            breakdown["services"].append(service_detail)
            breakdown["base_total"] += service.price
            breakdown["total_discount"] += service_detail["discount"]

        breakdown["final_total"] = breakdown["base_total"] - breakdown["total_discount"]
        return breakdown

    def has_coupon_codes(self):
        """Check if any service in the appointment has a coupon code"""
        return any(service.applied_coupon_code for service in self.services.all())

    def get_applied_coupon_codes(self):
        """Return list of all coupon codes applied to services"""
        return [
            service.applied_coupon_code
            for service in self.services.all()
            if service.applied_coupon_code
        ]

    def __str__(self):
        return f"{self.user.email} - {self.appointment_time} with {self.staff.email}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("credit_card", "Credit Card"),
        ("cash", "Cash"),
        ("mobile_payment", "Mobile Payment"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES)
    transaction_date = models.DateTimeField(auto_now_add=True)
