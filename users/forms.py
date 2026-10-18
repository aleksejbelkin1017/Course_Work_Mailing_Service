from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import User


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации по email с подтверждением пароля."""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)


class CustomAuthenticationForm(AuthenticationForm):
    """Форма входа по email."""
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True}),
    )
