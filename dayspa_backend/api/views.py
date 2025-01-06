import logging
from decimal import Decimal

import paypalrestsdk
import requests
from accounts.models import Role
from allauth.socialaccount.models import SocialAccount
from bookings.models import Appointment, Payment
from core import settings
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Sum
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from services.models import Coupon, Service
from weasyprint import HTML
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import io
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
    CashPaymentCreateSerializer,
    ErrorResponseSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    PayPalPaymentCreateSerializer,
    PayPalPaymentExecuteSerializer,
    RegisterSerializer,
    ServiceSerializer,
    UserChangePassword,
    UserSerializer,
    UserUpdateSerializer,
)
from rest_framework.exceptions import ValidationError
from .utils import api_response

logger = logging.getLogger("api.views")


def send_appointment_invoice(appointment):
    """
    Generate and send an invoice PDF for the given appointment
    """
    try:
        # Prepare invoice details
        services = appointment.services.all()
        total_price = appointment.calculate_total_price()

        # Render HTML invoice template
        html_string = render_to_string(
            "invoices/appointment_invoice.html",
            {
                "user": appointment.user,
                "appointment": appointment,
                "services": services,
                "total_price": total_price,
                "coupon": appointment.coupon
                if hasattr(appointment, "coupon")
                else None,
            },
        )

        # Generate PDF from HTML
        pdf_buffer = io.BytesIO()
        HTML(string=html_string).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)

        # Create and send email with PDF attachment
        email = EmailMessage(
            subject=f"Invoice for Appointment #{appointment.id}",
            body="Please find your appointment invoice attached.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[appointment.user.email],
        )

        # Attach PDF
        email.attach(
            f"invoice_{appointment.id}.pdf", pdf_buffer.getvalue(), "application/pdf"
        )

        # Send email
        email.send()

        logger.info(f"Invoice sent successfully for Appointment #{appointment.id}")

    except Exception as e:
        logger.error(
            f"Failed to send invoice for Appointment #{appointment.id}: {str(e)}"
        )


def verify_google_token(token):
    """Verify the Google ID token using Google's token info endpoint."""
    try:
        google_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        response = requests.get(google_url)
        if response.status_code == 200:
            return response.json()  # Returns the decoded token data
        else:
            logger.error(f"Failed to verify token with Google: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error verifying Google token: {e}")
        return None


class ServicePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class EmptySerializer(Serializer):
    """
    A placeholder serializer for schema generation
    """

    pass


class GoogleSignInView(APIView):
    """
    A View for handling Google sign-in and issuing JWT tokens.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle Google sign-in by verifying the token and issuing a JWT token.
        """
        token = request.data.get("token")
        if not token:
            return Response(
                {"success": False, "message": "Token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.debug(
            f"Received token: {token[:20]}..."
        )  # Log first 20 characters of the token for debugging

        # Verify the token using Google's API
        token_data = verify_google_token(token)
        if not token_data:
            return Response(
                {
                    "success": False,
                    "message": "Invalid token or unable to verify token",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.debug(f"Decoded Token Data: {token_data}")

        # Check if the user already exists based on the email in the token
        user = get_user_model().objects.filter(email=token_data.get("email")).first()

        if not user:
            # If user doesn't exist, create a new user
            logger.debug(
                f"User not found, creating new user with email: {token_data.get('email')}"
            )

            # Retrieve the 'Customer' role from the Role model
            customer_role = Role.objects.get(id=2)  # Assuming 2 is the Customer role

            # Create the user and assign the 'Customer' role
            user = get_user_model().objects.create_user(
                email=token_data.get("email"),
                first_name=token_data.get("given_name", ""),
                last_name=token_data.get("family_name", ""),
                user_role=customer_role,  # Assign the Role instance
            )

            # Create a new SocialAccount and link it to the user
            SocialAccount.objects.create(
                user=user, provider="google", extra_data=token_data
            )

            logger.debug(f"Created new user: {user.username}")

        # Log the user in (no further action required, user is already created or found)
        logger.debug(f"Authenticated user: {user.username}")

        # Issue JWT tokens for the authenticated user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Return user details along with the access and refresh tokens
        return Response(
            {
                "success": True,
                "message": "Google Sign-In successful",
                "data": {
                    "username": user.username,
                    "email": user.email,
                    "user_id": user.id,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            },
            status=status.HTTP_200_OK,
        )


class AuthViewSet(viewsets.ViewSet):
    """
    A ViewSet for handling authentication-related actions
    """

    @extend_schema(
        request=PasswordResetSerializer,
        responses={200: None, 400: ErrorResponseSerializer},
        description="Request a password reset link.",
    )
    @action(detail=False, methods=["post"])
    def password_reset(self, request):
        """
        Handle the password reset request by sending a reset email.
        """
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Sends the password reset email
            return api_response(
                success=True,
                message="Password reset email sent successfully",
                data=None,
                status_code=status.HTTP_200_OK,
            )
        return api_response(
            success=False,
            message="Failed to send password reset email",
            error_details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={200: None, 400: ErrorResponseSerializer},
        description="Confirm password reset and update the password.",
    )
    @action(detail=False, methods=["post"])
    def password_reset_confirm(self, request):
        """
        Handle the password reset confirmation with a new password.
        """
        token = request.data.get("token")

        # Remove email context
        serializer = PasswordResetConfirmSerializer(data=request.data)

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()  # Resets the password
                return api_response(
                    success=True,
                    message="Password has been successfully reset.",
                    data=None,
                    status_code=status.HTTP_200_OK,
                )
        except ErrorResponseSerializer:
            # This will catch validation errors from the serializer
            return api_response(
                success=False,
                message="Password reset failed",
                error_details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        request=UserUpdateSerializer,
        responses={200: UserSerializer, 400: ErrorResponseSerializer},
        description="Update the user's first and last name.",
    )
    @action(detail=False, methods=["put"], permission_classes=[IsAuthenticated])
    def update_user_info(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data)

        if serializer.is_valid():
            updated_user = serializer.save()  # Save the updated user data
            user_serializer = UserSerializer(
                updated_user
            )  # Serialize the updated user data
            return api_response(
                success=True,
                message="User information updated successfully",
                data={"user": user_serializer.data},
                status_code=status.HTTP_200_OK,
            )

        return api_response(
            success=False,
            message="Update failed",
            error_details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        request=UserChangePassword,
        responses={200: None, 400: ErrorResponseSerializer},
        description="Change the user's password.",
    )
    @action(detail=False, methods=["put"], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        Handle the request to change a user's password.
        """
        # Instantiate the serializer with the data from the request
        serializer = UserChangePassword(data=request.data)

        if serializer.is_valid():
            # Authenticate the user with the provided email and old password
            user = authenticate(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["old_password"],
            )

            if not user:
                raise ValidationError(
                    {"old_password": "The old password is incorrect."}
                )

            # Set the new password
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            # Optionally: you can log the user out after password change or invalidate sessions

            return api_response(
                success=True,
                message="Password changed successfully",
                data=None,
                status_code=status.HTTP_200_OK,
            )

        return api_response(
            success=False,
            message="Password change failed",
            error_details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserSerializer, 400: ErrorResponseSerializer},
        description="Register a new user with email, password, and other details.",
    )
    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_serializer = UserSerializer(user)
            return api_response(
                success=True,
                message="User registered successfully",
                data={"user": user_serializer.data},
                status_code=status.HTTP_201_CREATED,
            )
        return api_response(
            success=False,
            message="Registration failed",
            error_details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        request=LoginSerializer,  # Specifies the LoginSerializer for request body
        responses={201: UserSerializer, 400: ErrorResponseSerializer},
        description="Log in a user and return JWT tokens along with user details.",
        examples=[
            OpenApiExample(
                "Login Request",
                value={"email": "example@example.com", "password": "password123"},
                request_only=True,  # Indicates this is a request example
            ),
            OpenApiExample(
                "Login Response",
                value={
                    "access_token": "example_access_token",
                    "refresh_token": "example_refresh_token",
                    "user": {
                        "id": 1,
                        "email": "example@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "user_role": "user",
                        "created_at": "2024-11-27T12:34:56Z",
                    },
                },
            ),
        ],
    )
    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            user_serializer = UserSerializer(user)

            return api_response(
                success=True,
                message="Login successful",
                data={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": user_serializer.data,
                },
                status_code=status.HTTP_200_OK,
            )

        return api_response(
            success=False,
            message="Invalid credentials",
            error_details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        responses={200: UserSerializer},
        description="Retrieve the authenticated user's details.",
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return api_response(
            success=True,
            message="User retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        request=None,
        responses={200: None, 400: ErrorResponseSerializer},
        description="Log out a user by blacklisting the refresh token.",
        examples=[
            OpenApiExample(
                "Successful Logout Response",
                value={
                    "success": True,
                    "message": "Logout successful",
                },
            )
        ],
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Log out the user by blacklisting their refresh token.
        """
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return api_response(
                success=False,
                message="Refresh token is required to log out",
                error_details={"refresh_token": ["This field is required."]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return api_response(
                success=True,
                message="Logout successful",
                data=None,
                status_code=status.HTTP_200_OK,
            )
        except TokenError as e:
            return api_response(
                success=False,
                message="Invalid or expired token",
                error_details={"refresh_token": [str(e)]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for listing and retrieving services.
    """

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]
    pagination_class = ServicePagination

    @extend_schema(
        responses={
            200: ServiceSerializer(many=True),
            400: ErrorResponseSerializer,
        },
        description="Retrieve a paginated list of available services.",
    )
    def list(self, request, *args, **kwargs):
        """
        Retrieve a paginated list of all services.
        """
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return api_response(
                success=True,
                message="Services retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return api_response(
                success=False,
                message="Failed to retrieve services",
                error_details={"error": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        responses={
            200: ServiceSerializer,
            400: ErrorResponseSerializer,
        },
        description="Retrieve the details of a specific service by its ID.",
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve details of a specific service.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return api_response(
                success=True,
                message="Service retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return api_response(
                success=False,
                message="Failed to retrieve service details",
                error_details={"error": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )


class AppointmentViewSet(viewsets.ViewSet):
    """
    A ViewSet for handling appointment-related actions, allowing only authenticated users
    to create, update, delete, and retrieve appointments.
    """

    @extend_schema(
        request=AppointmentCreateSerializer,
        responses={201: AppointmentCreateSerializer, 400: ErrorResponseSerializer},
        description="Create a new appointment with user details and selected services.",
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def create_appointment(self, request):
        """
        Creates an appointment for an authenticated user, with optional coupon application.
        """
        # Extract coupon code from request data
        coupon_code = request.data.get("coupon_code")
        coupon = None

        # Validate coupon if provided
        if coupon_code:
            try:
                current_time = timezone.now()
                coupon = Coupon.objects.get(
                    coupon_code=coupon_code,
                    valid_from__lte=current_time,
                    valid_until__gte=current_time,
                )
            except Coupon.DoesNotExist:
                return api_response(
                    success=False,
                    message="Invalid or expired coupon code",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        serializer_context = {
            "request": request,
            "coupon": coupon,  # Pass coupon to serializer context
        }

        serializer = AppointmentCreateSerializer(
            data=request.data, context=serializer_context
        )

        if serializer.is_valid():
            appointment = serializer.save()

            if coupon:
                appointment.coupon = coupon
                appointment.save()

            # Send invoice asynchronously (recommended for production)
            # You can use Celery or Django's background tasks for this
            try:
                send_appointment_invoice(appointment)
            except Exception as e:
                # Log the error, but don't prevent appointment creation
                logger.error(f"Invoice sending failed: {str(e)}")

            return api_response(
                success=True,
                message="Appointment created successfully",
                data=AppointmentCreateSerializer(appointment).data,
                status_code=status.HTTP_201_CREATED,
            )

        return api_response(
            success=False,
            message="Appointment creation failed",
            error_details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        responses={200: AppointmentSerializer(many=True)},
        description="Retrieve all appointments for a specific user. If no user_id is provided, fetch appointments for the authenticated user.",
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def list_appointments(self, request):
        """
        Retrieve appointments made by a specific user.
        If no user_id is provided, fetch appointments for the authenticated user.
        """
        user_id = request.query_params.get("user_id", None)

        if user_id:
            if str(request.user.id) != user_id and not request.user.is_staff:
                raise NotFound(
                    "You do not have permission to access this user's appointments."
                )
            appointments = Appointment.objects.filter(user_id=user_id)
        else:
            appointments = Appointment.objects.filter(user=request.user)

        if not appointments.exists():
            raise NotFound("No appointments found for this user.")

        serializer = AppointmentSerializer(appointments, many=True)
        return api_response(
            success=True,
            message="Appointments retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        request=AppointmentSerializer,
        responses={200: AppointmentSerializer, 400: ErrorResponseSerializer},
        description="Update an appointment by ID.",
        parameters=[
            OpenApiParameter(name="id", type=int, location=OpenApiParameter.PATH)
        ],
    )
    @action(detail=True, methods=["put"], permission_classes=[IsAuthenticated])
    def update_appointment(self, request, pk: int):
        """
        Update an existing appointment by its ID.
        """
        try:
            appointment = Appointment.objects.get(pk=pk, user=request.user)
        except Appointment.DoesNotExist:
            raise NotFound("Appointment not found.")

        serializer = AppointmentSerializer(appointment, data=request.data)

        if serializer.is_valid():
            appointment = serializer.save()
            return api_response(
                success=True,
                message="Appointment updated successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )

        return api_response(
            success=False,
            message="Appointment update failed",
            error_details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def validate_coupon(self, request):
        """
        Validate a coupon and calculate the discounted price for the services in the cart.

        Expected request data:
        {
            "services": [...],  # List of service IDs
            "coupon_code": "OPTIONAL_COUPON_CODE"
        }
        """
        # Extract services and coupon code from request
        service_ids = request.data.get("services", [])
        coupon_code = request.data.get("coupon_code")

        # Validate services exist
        services = Service.objects.filter(id__in=service_ids)
        if not services.exists():
            return api_response(
                success=False,
                message="Invalid services selected",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate base total
        base_total = services.aggregate(total=Sum("price"))["total"] or Decimal("0")

        # If no coupon code provided, return base total
        if not coupon_code:
            return api_response(
                success=True,
                message="No coupon applied",
                data={
                    "base_total": base_total,
                    "final_total": base_total,
                    "discount_percentage": Decimal("0"),
                    "discount_amount": Decimal("0"),
                },
                status_code=status.HTTP_200_OK,
            )

        # Validate coupon
        try:
            current_time = timezone.now()
            coupon = Coupon.objects.get(
                coupon_code=coupon_code,
                valid_from__lte=current_time,
                valid_until__gte=current_time,
            )
        except Coupon.DoesNotExist:
            return api_response(
                success=False,
                message="Invalid or expired coupon code",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate discount
        discount_amount = base_total * coupon.discount / Decimal("100")
        final_total = base_total - discount_amount

        return api_response(
            success=True,
            message="Coupon applied successfully",
            data={
                "base_total": base_total,
                "final_total": final_total,
                "discount_percentage": coupon.discount,
                "discount_amount": discount_amount,
                "coupon_code": coupon.coupon_code,
            },
            status_code=status.HTTP_200_OK,
        )


class PayPalPaymentViewSet(viewsets.GenericViewSet):
    """
    ViewSet for handling PayPal payments
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer  # Placeholder serializer for schema generation

    @action(
        detail=False, methods=["POST"], serializer_class=PayPalPaymentCreateSerializer
    )
    def create_payment(self, request):
        """
        Create a PayPal payment
        """
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return api_response(
                success=False,
                message="Invalid payment details",
                error_details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        appointment_id = serializer.validated_data["appointment_id"]
        currency = serializer.validated_data.get("currency", "USD")

        # Fetch appointment and calculate total amount
        appointment = Appointment.objects.get(id=appointment_id)

        # Initialize item total and items list
        item_total = Decimal("0")
        items = []

        for service in appointment.services.all():
            # Use base price (before any discount) for the item price
            service_price = service.price
            item_total += service_price  # Adding base price to item total

            # Add the item to the PayPal items list
            items.append(
                {
                    "name": service.service_name,
                    "price": "{:.2f}".format(service_price),  # Base price for PayPal
                    "currency": currency,
                    "quantity": 1,
                }
            )

        # Get the final total price after discounts
        final_total_price = (
            appointment.calculate_total_price()
        )  # Final total after discount

        # Log both values for debugging
        print(f"Item Total (before discount): {item_total}")
        print(f"Final Total (after discount): {final_total_price}")

        # Ensure that item total matches the final total price
        if item_total != final_total_price:
            return api_response(
                success=False,
                message=f"Item prices ({item_total}) do not match the calculated total ({final_total_price}).",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Configure PayPal SDK
            paypalrestsdk.configure(
                {
                    "mode": settings.PAYPAL_MODE,
                    "client_id": settings.PAYPAL_CLIENT_ID,
                    "client_secret": settings.PAYPAL_CLIENT_SECRET,
                }
            )

            # Create PayPal payment
            payment = paypalrestsdk.Payment(
                {
                    "intent": "sale",
                    "payer": {"payment_method": "paypal"},
                    "redirect_urls": {
                        "return_url": settings.PAYPAL_RETURN_URL,
                        "cancel_url": settings.PAYPAL_CANCEL_URL,
                    },
                    "transactions": [
                        {
                            "amount": {
                                "total": "{:.2f}".format(
                                    final_total_price
                                ),  # Total after discount
                                "currency": currency,
                            },
                            "description": f"Payment for Appointment #{appointment_id}",
                            "item_list": {
                                "items": items  # The itemized list with base prices
                            },
                        }
                    ],
                }
            )

            if payment.create():
                # Update Appointment status to "pending"
                appointment.status = "pending"
                appointment.save()

                # Get the approval URL
                for link in payment.links:
                    if link.rel == "approval_url":
                        return api_response(
                            success=True,
                            message="Payment created successfully",
                            data={"payment_id": payment.id, "approval_url": link.href},
                            status_code=status.HTTP_201_CREATED,
                        )

            return api_response(
                success=False,
                message="Failed to create PayPal payment",
                error_details=payment.error,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return api_response(
                success=False,
                message="Error processing payment",
                error_details=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        detail=False, methods=["POST"], serializer_class=PayPalPaymentExecuteSerializer
    )
    def execute_payment(self, request):
        """
        Execute a PayPal payment
        """
        print(f"Request headers: {request.headers}")
        print(f"Authentication: {request.user}")

        print(f"Is authenticated: {request.user.is_authenticated}")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return api_response(
                success=False,
                message="Invalid payment execution details",
                error_details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        payment_id = serializer.validated_data["payment_id"]
        payer_id = serializer.validated_data["payer_id"]

        try:
            # Retrieve the payment from PayPal
            payment = paypalrestsdk.Payment.find(payment_id)

            if payment.execute({"payer_id": payer_id}):
                # Update appointment status to "confirmed" after successful payment
                appointment_id = payment.transactions[0]["description"].split("#")[-1]
                appointment = Appointment.objects.get(id=appointment_id)
                appointment.status = "confirmed"
                appointment.save()

                # Create a Payment record
                Payment.objects.create(
                    appointment=appointment,
                    user=request.user,
                    amount=Decimal(payment.transactions[0]["amount"]["total"]),
                    payment_method="paypal",
                    payment_status="completed",
                )

                return api_response(
                    success=True,
                    message="Payment executed successfully",
                    data={"payment_id": payment.id, "state": payment.state},
                    status_code=status.HTTP_200_OK,
                )

            return api_response(
                success=False,
                message="Failed to execute payment",
                error_details=payment.error,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return api_response(
                success=False,
                message="Error executing payment",
                error_details=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CashPaymentViewSet(viewsets.GenericViewSet):
    """
    ViewSet for handling Cash payments
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CashPaymentCreateSerializer

    @action(detail=False, methods=["POST"])
    def create_cash_payment(self, request):
        """
        Create a cash payment for an appointment
        """
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return api_response(
                success=False,
                message="Invalid payment details",
                error_details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        appointment_id = serializer.validated_data["appointment_id"]

        try:
            # Fetch appointment and calculate total amount
            appointment = Appointment.objects.get(id=appointment_id)
            total_amount = appointment.calculate_total_price()

            # Create Payment record
            payment = Payment.objects.create(
                appointment=appointment,
                user=request.user,
                amount=total_amount,
                payment_method="cash",
                payment_status="pending",  # Assuming cash is marked as completed immediately
            )

            # Update appointment status
            appointment.status = "pending"
            appointment.save()

            return api_response(
                success=True,
                message="Cash payment recorded successfully",
                data={
                    "payment_id": payment.id,
                    "amount": str(total_amount),
                    "payment_method": "cash",
                },
                status_code=status.HTTP_200_OK,
            )

        except Appointment.DoesNotExist:
            return api_response(
                success=False,
                message="Appointment not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return api_response(
                success=False,
                message="Error processing cash payment",
                error_details=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
