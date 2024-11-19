from django.db import models
from django.utils import timezone
from django.conf import settings  # Add this for User model reference


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
    )  # Fixed reference
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


class StaffProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )  # Fixed reference
    bio = models.TextField(blank=True)
    services = models.ManyToManyField(
        "services.Service", through="services.StaffService"
    )  # Fixed reference
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class StaffService(models.Model):
    """
    Simple intermediate model to track which staff can perform which services
    """

    staff = models.ForeignKey(
        "services.StaffProfile", on_delete=models.CASCADE
    )  # Fixed reference
    service = models.ForeignKey(
        "services.Service", on_delete=models.CASCADE
    )  # Fixed reference

    class Meta:
        unique_together = ("staff", "service")

    def __str__(self):
        return f"{self.staff} - {self.service.service_name}"
