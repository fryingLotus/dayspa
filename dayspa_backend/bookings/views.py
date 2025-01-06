# booking/views.py
from django.views.generic import CreateView
from .utils import is_time_slot_available, book_appointment


class AppointmentCreateView(CreateView):
    def form_valid(self, form):
        # Get form data
        staff = form.cleaned_data["staff"]
        services = form.cleaned_data["services"]
        appointment_time = form.cleaned_data["appointment_time"]

        try:
            # Attempt to book appointment
            appointment = book_appointment(
                customer=self.request.user,
                staff=staff,
                services=services,
                appointment_time=appointment_time,
            )
            return super().form_valid(form)
        except ValueError as e:
            # Handle unavailable time slot
            form.add_error(None, str(e))
            return self.form_invalid(form)
