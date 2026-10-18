from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from mailing.models import Mailing, Message, Recipient
from mailing.services import send_mailing


# --- RECIPIENT ---

class RecipientListView(LoginRequiredMixin, ListView):
    """Страница со списком всех получателей."""
    model = Recipient
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipients"


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """Страница создания нового получателя."""
    model = Recipient
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")
    extra_context = {"title": "Добавить получателя", "button_text": "Создать"}

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    """Страница редактирования существующего получателя."""
    model = Recipient
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")
    extra_context = {"title": "Редактировать получателя", "button_text": "Сохранить"}


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    """Страница подтверждения удаления получателя."""
    model = Recipient
    template_name = "mailing/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")


# --- MESSAGE ---

class MessageListView(LoginRequiredMixin, ListView):
    """Страница со списком всех сообщений."""
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Страница создания нового сообщения."""
    model = Message
    fields = ["subject", "body"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")
    extra_context = {"title": "Добавить сообщение", "button_text": "Создать"}

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """Страница редактирования существующего сообщения."""
    model = Message
    fields = ["subject", "body"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")
    extra_context = {"title": "Редактировать сообщение", "button_text": "Сохранить"}


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """Страница подтверждения удаления сообщения."""
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")


# --- MAILING ---

class MailingListView(LoginRequiredMixin, ListView):
    """Страница со списком всех рассылок."""
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Страница создания новой рассылки."""
    model = Mailing
    fields = ["start_time", "end_time", "message", "recipients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")
    extra_context = {"title": "Добавить рассылку", "button_text": "Создать"}

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    """Страница редактирования существующей рассылки."""
    model = Mailing
    fields = ["start_time", "end_time", "message", "recipients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")
    extra_context = {"title": "Редактировать рассылку", "button_text": "Сохранить"}


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """Страница подтверждения удаления рассылки."""
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MailingSendView(LoginRequiredMixin, View):
    """Запуск рассылки по требованию."""

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        success, message = send_mailing(mailing)

        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

        return redirect("mailing:mailing_list")


# --- INDEX ---

class IndexView(View):
    """Главная страница со статистикой."""

    def get(self, request):
        total_mailings = Mailing.objects.count()
        active_mailings = Mailing.objects.filter(
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now(),
            status=Mailing.STATUS_STARTED,
        ).count()
        total_recipients = Recipient.objects.count()

        context = {
            "total_mailings": total_mailings,
            "active_mailings": active_mailings,
            "total_recipients": total_recipients,
        }
        from django.shortcuts import render
        return render(request, "mailing/index.html", context)
