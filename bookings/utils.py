from django.db.models import Q
from datetime import timedelta
from .models import Appointment


def is_time_slot_available(staff, appointment_time, duration):
    """
    Check if a time slot is available for a specific staff member.

    Args:
        staff (User): Staff member to check availability for
        appointment_time (datetime): Proposed appointment start time
        duration (int): Total duration of services in minutes

    Returns:
        bool: True if slot is available, False otherwise
    """
    conflicting_appointments = Appointment.objects.filter(
        staff=staff, status__in=["confirmed", "in_progress"]
    ).filter(
        Q(
            # New appointment starts during an existing appointment
            appointment_time__range=(
                appointment_time,
                appointment_time + timedelta(minutes=duration),
            )
        )
        | Q(
            # Existing appointment overlaps with new appointment
            appointment_time__lte=appointment_time,
            appointment_time__gt=(appointment_time - timedelta(minutes=duration)),
        )
    )

    return not conflicting_appointments.exists()


def book_appointment(customer, staff, services, appointment_time):
    """
    Book an appointment with availability checking.

    Args:
        customer (User): Customer booking the appointment
        staff (User): Staff member for the appointment
        services (list): List of services to be performed
        appointment_time (datetime): Proposed appointment time

    Raises:
        ValueError: If time slot is not available

    Returns:
        Appointment: Created appointment object
    """
    # Calculate total duration of services
    total_duration = sum(service.duration for service in services)

    # Check staff availability
    if not is_time_slot_available(staff, appointment_time, total_duration):
        raise ValueError("Selected time slot is not available")

    # Create appointment
    appointment = Appointment.objects.create(
        user=customer,
        staff=staff,
        appointment_time=appointment_time,
        status="confirmed",
    )

    # Add services to appointment
    appointment.services.add(*services)

    return appointment
