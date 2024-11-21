from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.conf import settings  # Add this for User model reference

from accounts.models import User


class Coupon(models.Model):
    coupon_code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.coupon_code} ({self.discount}% off)"


class Service(models.Model):
    service_name = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(
        "services.Coupon", on_delete=models.SET_NULL, null=True, blank=True
    )
    service_image = models.ImageField(upload_to="services/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    applied_coupon_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Coupon code entered by user for this service",
    )

    def apply_coupon(self, coupon_code):
        try:
            coupon = Coupon.objects.get(
                coupon_code=coupon_code,
                valid_from__lte=timezone.now(),
                valid_until__gte=timezone.now(),
            )
            self.coupon = coupon
            self.applied_coupon_code = coupon_code
            self.save()
            return True
        except Coupon.DoesNotExist:
            return False

    def __str__(self):
        return self.service_name
class StaffService(models.Model):
    staff = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('staff', 'service')
