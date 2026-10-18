from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from mailing.models import Recipient


class RecipientListView(ListView):
    """Страница со списком всех получателей."""
    model = Recipient
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipients"


class RecipientCreateView(CreateView):
    """Страница создания нового получателя."""
    model = Recipient
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")
    extra_context = {"title": "Добавить получателя", "button_text": "Создать"}


class RecipientUpdateView(UpdateView):
    """Страница редактирования существующего получателя."""
    model = Recipient
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")
    extra_context = {"title": "Редактировать получателя", "button_text": "Сохранить"}


class RecipientDeleteView(DeleteView):
    """Страница подтверждения удаления получателя."""
    model = Recipient
    template_name = "mailing/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")