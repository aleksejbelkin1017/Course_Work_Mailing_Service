from django.urls import reverse_lazy
from django.views.generic import CreateView
from users.forms import CustomUserCreationForm


class RegisterView(CreateView):
    """Регистрация нового пользователя."""
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")
