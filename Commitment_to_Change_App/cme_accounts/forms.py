from django.forms import ModelForm, TextInput

from .models import User


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password"
        ]
        widgets = {
            "password": TextInput(attrs={"type": "password"})
        }
