from django.db import models
from django.db.models import Sum, Q
from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from accounts.models import User  # Import User from the accounts app
from services.models import (
    Service,
    StaffService,
)  # Import Service from the services app


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("pending", "Pending"),
        ("canceled", "Canceled"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="client_appointments",
        limit_choices_to=Q(user_role__role_name="Customer"),
    )
    services = models.ManyToManyField(Service, related_name="appointments")
    appointment_time = models.DateTimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey(
        "services.Coupon",  # Corrected to reference the 'services' app
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="appointments",
    )

    def calculate_total_price(self):
        base_total = self.services.aggregate(total=Sum("price"))["total"] or Decimal(
            "0"
        )
        total_discount = Decimal("0")
        current_time = timezone.now()  # This returns a timezone-aware datetime

        # Ensure the coupon's datetime fields are timezone-aware
        if self.coupon:
            valid_from = self.coupon.valid_from
            valid_until = self.coupon.valid_until

            # Ensure coupon datetime fields are timezone-aware
            if valid_from and valid_from.tzinfo is None:
                valid_from = timezone.make_aware(valid_from)

            if valid_until and valid_until.tzinfo is None:
                valid_until = timezone.make_aware(valid_until)

            # Compare timezone-aware datetimes
            if valid_from <= current_time <= valid_until:
                total_discount = base_total * self.coupon.discount / Decimal("100")

        final_price = base_total - total_discount
        return max(final_price, Decimal("0"))

    def get_price_breakdown(self):
        breakdown = {
            "services": [],
            "base_total": Decimal("0"),
            "total_discount": Decimal("0"),
            "final_total": Decimal("0"),
            "applied_coupon": None,  # To show the coupon applied to the whole appointment
        }

        current_time = timezone.now()  # This returns a timezone-aware datetime

        for service in self.services.all():
            service_detail = {
                "name": service.service_name,
                "price": service.price,
                "discount": Decimal("0"),
            }

            # Ensure the service's coupon datetime fields are timezone-aware
            if service.coupon:
                valid_from = service.coupon.valid_from
                valid_until = service.coupon.valid_until

                if valid_from and valid_from.tzinfo is None:
                    valid_from = timezone.make_aware(valid_from)

                if valid_until and valid_until.tzinfo is None:
                    valid_until = timezone.make_aware(valid_until)

                # Compare timezone-aware datetimes
                if valid_from <= current_time <= valid_until:
                    service_detail["discount"] = (
                        service.price * service.coupon.discount / Decimal("100")
                    )
                    service_detail["coupon_code"] = service.coupon.coupon_code

            breakdown["services"].append(service_detail)
            breakdown["base_total"] += service.price
            breakdown["total_discount"] += service_detail["discount"]

        # Apply the appointment-wide coupon discount if available
        if self.coupon:
            valid_from = self.coupon.valid_from
            valid_until = self.coupon.valid_until

            if valid_from and valid_from.tzinfo is None:
                valid_from = timezone.make_aware(valid_from)

            if valid_until and valid_until.tzinfo is None:
                valid_until = timezone.make_aware(valid_until)

            if valid_from <= current_time <= valid_until:
                breakdown["applied_coupon"] = self.coupon.coupon_code
                breakdown["total_discount"] += (
                    breakdown["base_total"] * self.coupon.discount / Decimal("100")
                )

        breakdown["final_total"] = breakdown["base_total"] - breakdown["total_discount"]
        return breakdown

    def has_coupon_codes(self):
        # This method checks if there is any coupon applied to the services or the appointment itself
        return bool(self.coupon) or any(
            service.applied_coupon_code for service in self.services.all()
        )

    def get_applied_coupon_codes(self):
        # This method retrieves the coupon codes applied to the appointment and services
        applied_coupons = []
        if self.coupon:
            applied_coupons.append(self.coupon.coupon_code)
        applied_coupons.extend(
            service.applied_coupon_code
            for service in self.services.all()
            if service.applied_coupon_code
        )
        return applied_coupons

    def __str__(self):
        return f"{self.user.email} - {self.appointment_time}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("credit_card", "Credit Card"),
        ("cash", "Cash"),
        ("mobile_payment", "Mobile Payment"),
        ("paypal", "PayPal"),  # Add PayPal to the choices
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

    # Add PayPal-specific fields
    payment_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    payer_id = models.CharField(max_length=255, null=True, blank=True)


@receiver(post_save, sender=Appointment)
def assign_staff_to_appointment(sender, instance, created, **kwargs):
    if created:
        # Find primary staff for the services
        primary_staff = StaffService.objects.filter(
            service__in=instance.services.all(), is_primary=True
        ).first()

        # If no primary staff, find any available staff for the services
        if not primary_staff:
            primary_staff = StaffService.objects.filter(
                service__in=instance.services.all()
            ).first()

        # If staff found, create an AppointmentStaff record
        if primary_staff:
            AppointmentStaff.objects.create(
                appointment=instance, staff=primary_staff.staff
            )
        else:
            # Optional: You might want to handle the case when no staff is found
            # This could be logging, sending an notification, etc.
            pass


class AppointmentStaff(models.Model):
    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, related_name="appointment_staff"
    )
    staff = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="assigned_appointments"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("appointment", "staff")

    def __str__(self):
        return f"{self.appointment} - {self.staff}"
