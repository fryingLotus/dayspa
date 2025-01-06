from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import GoogleSignInView
from .views import (
    AuthViewSet,
    ServiceViewSet,
    AppointmentViewSet,
    PayPalPaymentViewSet,
    CashPaymentViewSet,
)

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"service", ServiceViewSet, basename="service")
router.register(r"appointments", AppointmentViewSet, basename="appointments")
router.register(r"paypal", PayPalPaymentViewSet, basename="paypal")
router.register(r"cash", CashPaymentViewSet, basename="cash")
urlpatterns = [
    # ViewSet routes
    path("", include(router.urls)),
    # SimpleJWT token views (if you want to keep them)
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("google/", GoogleSignInView.as_view(), name="google-signin"),
]
