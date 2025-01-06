from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from accounts.models import User, Role
from bookings.models import Appointment
from services.models import Service, Coupon
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email.")
        return value

    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        reset_url = (
            f"http://localhost:3000/reset-password/{token}/"  # Adjust URL as needed
        )
        send_mail(
            "Password Reset Request",
            f"To reset your password, click the link: {reset_url}",
            "no-reply@yourdomain.com",
            [user.email],
        )
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True, required=True, min_length=8, style={"input_type": "password"}
    )
    token = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        try:
            from django.contrib.auth.password_validation import validate_password

            validate_password(attrs["password"])
        except Exception as e:
            raise serializers.ValidationError({"password": list(e)})

        return attrs

    def validate_token(self, value):
        """
        Custom token validation method
        """
        from django.contrib.auth.tokens import default_token_generator

        for user in User.objects.all():
            if default_token_generator.check_token(user, value):
                self.context["reset_user"] = user
                return value

        raise serializers.ValidationError("Invalid or expired token")

    def save(self):
        user = self.context.get("reset_user")
        if not user:
            raise serializers.ValidationError("No user found for this token")

        user.set_password(self.validated_data["password"])
        user.save()
        return user


# User Serializer (for viewing user data)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "user_role", "created_at")
        read_only_fields = ("created_at",)


class UserUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)

    class Meta:
        model = User
        fields = ["first_name", "last_name"]  # Only the fields we want to update

    def update(self, instance, validated_data):
        # Update the user's first and last name
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()
        return instance


class UserChangePassword(serializers.ModelSerializer):
    email = serializers.CharField(required=True, max_length=100)
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User  # Specify the User model here
        fields = ["email", "old_password", "new_password"]

    def validate(self, attrs):
        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")

        if old_password == new_password:
            raise serializers.ValidationError(
                "New password cannot be the same as the old password."
            )

        return attrs


class GoogleSignInSerializer(serializers.Serializer):
    token = serializers.CharField()


# Register Serializer (for user registration)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    user_role = serializers.ChoiceField(
        choices=[(1, "Staff"), (2, "Customer")], required=False
    )

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "user_role",
        )

    def validate(self, data):
        """
        Check if the passwords match and validate the password.
        """
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords must match.")

        try:
            validate_password(data["password"])  # Validates the password strength
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        return data

    def create(self, validated_data):
        """
        Create a new user instance.
        """
        validated_data.pop("password2")

        # Get the user role by the numeric value
        user_role_value = validated_data.get(
            "user_role", 2
        )  # Default to 'Customer' (role_value = 2)
        user_role = Role.objects.get(
            role_name="Customer" if user_role_value == 2 else "Staff"
        )

        user = User(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            user_role=user_role,
        )
        user.set_password(validated_data["password"])
        user.save()

        return user


# Login Serializer (for authenticating users)
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        """
        Authenticate user credentials.
        """
        email = data.get("email")
        password = data.get("password")

        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")

        return user


# Service Serializer
class ServiceSerializer(serializers.ModelSerializer):
    service_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            "id",
            "service_name",
            "description",
            "duration",
            "price",
            "service_image_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_service_image_url(self, obj):
        request = self.context.get("request")
        if obj.service_image and request:
            return request.build_absolute_uri(obj.service_image.url)
        return None


class AppointmentCreateSerializer(serializers.ModelSerializer):
    services = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), many=True
    )
    coupon = serializers.PrimaryKeyRelatedField(
        queryset=Coupon.objects.all(), required=False, allow_null=True
    )
    status = serializers.ChoiceField(
        choices=Appointment.STATUS_CHOICES, default="pending"
    )  # Default set to 'pending'

    class Meta:
        model = Appointment
        fields = ["id", "user", "services", "appointment_time", "status", "coupon"]

    def create(self, validated_data):
        # Pop services and coupon from validated_data to avoid direct assignment
        services_data = validated_data.pop("services", [])
        coupon_data = validated_data.pop("coupon", None)

        # Create the appointment without services and coupon first
        appointment = Appointment.objects.create(**validated_data)

        # Set services using .set() method
        if services_data:
            appointment.services.set(services_data)

        # Set coupon if provided
        if coupon_data:
            appointment.coupon = coupon_data

        appointment.save()
        return appointment


class AppointmentSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True)
    coupon = serializers.SerializerMethodField()
    status = serializers.ChoiceField(choices=Appointment.STATUS_CHOICES)
    coupon_code = serializers.CharField(
        write_only=True, required=False, allow_null=True
    )
    payment_method = serializers.SerializerMethodField()

    # Total price method field
    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_total_price(self, instance):
        return instance.calculate_total_price()

    # Coupon method field
    @extend_schema_field(serializers.DictField(allow_null=True))
    def get_coupon(self, instance):
        # If no coupon is applied, return None
        if not instance.coupon:
            return None

        # Return coupon details
        current_time = timezone.now()
        is_valid = (
            instance.coupon.valid_from <= current_time <= instance.coupon.valid_until
        )

        return {
            "id": instance.coupon.id,
            "display_name": str(instance.coupon),
            "coupon_code": instance.coupon.coupon_code,
            "discount": instance.coupon.discount,
            "is_valid": is_valid,
        }

    @extend_schema_field(serializers.CharField(required=False, allow_null=True))
    def get_payment_method(self, instance):
        payment = instance.payment_set.first()
        if payment:
            return payment.payment_method

    # Price breakdown method field
    @extend_schema_field(serializers.DictField())
    def get_price_breakdown(self, instance):
        return instance.get_price_breakdown()

    # Declare method fields
    total_price = serializers.SerializerMethodField()
    price_breakdown = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id",
            "user",
            "services",
            "appointment_time",
            "status",
            "coupon",
            "total_price",
            "price_breakdown",
            "created_at",
            "coupon_code",
            "payment_method",
        ]

    def validate(self, data):
        """
        Validate coupon code if provided
        """
        coupon_code = data.get("coupon_code")

        if coupon_code:
            try:
                current_time = timezone.now()
                coupon = Coupon.objects.get(
                    coupon_code=coupon_code,
                    valid_from__lte=current_time,
                    valid_until__gte=current_time,
                )

                # Optional: Add additional coupon validation
                # For example, check minimum purchase amount
                services = data.get("services", [])
                total_services_price = sum(service.price for service in services)

                # Check if there's a minimum purchase requirement
                if hasattr(coupon, "minimum_purchase_amount"):
                    if total_services_price < coupon.minimum_purchase_amount:
                        raise serializers.ValidationError(
                            {
                                "coupon_code": f"Coupon requires a minimum purchase of {coupon.minimum_purchase_amount}"
                            }
                        )

                # Attach coupon to context for use in create/update methods
                self.coupon = coupon

            except Coupon.DoesNotExist:
                raise serializers.ValidationError(
                    {"coupon_code": "Invalid or expired coupon code"}
                )

        return data

    def create(self, validated_data):
        """
        Custom create method to handle appointment creation with optional coupon
        """
        # Remove coupon_code from validated data
        validated_data.pop("coupon_code", None)

        # Extract services
        services = validated_data.pop("services", [])

        # Create appointment
        appointment = Appointment.objects.create(**validated_data)

        # Add services
        if services:
            appointment.services.set(services)

        # Add coupon if validated in the validation step
        if hasattr(self, "coupon"):
            appointment.coupon = self.coupon
            appointment.save()

        return appointment

    def update(self, instance, validated_data):
        """
        Custom update method to handle appointment updates with optional coupon
        """
        # Handle services
        services = validated_data.pop("services", None)
        if services is not None:
            instance.services.set(services)

        # Handle coupon
        if hasattr(self, "coupon"):
            instance.coupon = self.coupon

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Override to customize the representation of the serializer
        """
        representation = super().to_representation(instance)

        # Optional: Add any custom transformations
        # For example, formatting dates or adding computed fields
        return representation


class PayPalPaymentCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a PayPal payment
    """

    appointment_id = serializers.IntegerField(
        required=True,
        help_text="The ID of the appointment for which the payment is being made",
    )
    currency = serializers.CharField(
        max_length=3,
        default="USD",
        help_text="The currency for the payment (default: USD)",
    )

    def validate_appointment_id(self, value):
        """
        Validate that the appointment exists and belongs to the requesting user
        """
        user = self.context["request"].user
        try:
            appointment = Appointment.objects.get(id=value, user=user)
            if appointment.status != "pending":
                raise serializers.ValidationError(
                    "Only pending appointments can be paid."
                )
            return value
        except Appointment.DoesNotExist:
            raise serializers.ValidationError("Appointment not found.")

    def to_representation(self, instance):
        """
        Return details about the appointment and calculated total amount
        """
        appointment = Appointment.objects.get(id=self.validated_data["appointment_id"])

        # Get the total price of the appointment after discounts
        total_price = appointment.calculate_total_price()

        # If necessary, calculate price breakdown (itemized price)
        items = []
        item_total = Decimal("0")

        for service in appointment.services.all():
            service_price = service.price
            item_total += service_price
            items.append(
                {
                    "name": service.service_name,
                    "price": "{:.2f}".format(service_price),
                    "currency": self.validated_data.get("currency", "USD"),
                    "quantity": 1,
                }
            )

        # Ensure that the total price matches the item total
        if item_total != total_price:
            raise serializers.ValidationError(
                "The total item price does not match the calculated total price."
            )

        # Return representation with the appointment details and total amount
        return {
            "appointment_id": appointment.id,
            "total_amount": "{:.2f}".format(
                total_price
            ),  # Ensure the discounted price is used
            "currency": self.validated_data.get("currency", "USD"),
            "items": items,
        }


class PayPalPaymentExecuteSerializer(serializers.Serializer):
    """
    Serializer for executing a PayPal payment
    """

    payment_id = serializers.CharField(required=True, help_text="The PayPal payment ID")
    payer_id = serializers.CharField(required=True, help_text="The PayPal payer ID")


class CashPaymentCreateSerializer(serializers.Serializer):
    appointment_id = serializers.IntegerField()


class ErrorResponseSerializer(serializers.Serializer):
    """
    Serializer for standardizing the error response format.
    """

    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField(child=serializers.CharField())
    status_code = serializers.IntegerField()
