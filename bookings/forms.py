from django import forms
from .models import Appointment
from accounts.models import User


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = "__all__"

    # Override the staff field to filter users by the 'staff' role
    staff = forms.ModelChoiceField(
        queryset=User.objects.filter(user_role__role_name="staff"),
        required=True,
        empty_label=None,  # Do not allow empty selection
        label="Staff",
    )
