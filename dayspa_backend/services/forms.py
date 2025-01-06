from django import forms
from .models import StaffProfile
from accounts.models import User, Role


class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        customer_role = Role.objects.filter(role_name="Customer").first()
        if customer_role:
            self.fields["user"].queryset = User.objects.exclude(user_role=customer_role)
