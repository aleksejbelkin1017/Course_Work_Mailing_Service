from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from mailing.models import Mailing, Message, Recipient, Attempt
from mailing.services import send_mailing


class OwnerQuerysetMixin:
    """
    Миксин для фильтрации.
    Если пользователь не менеджер и не суперюзер — он видит только свои записи.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Менеджеры").exists():
            return qs
        return qs.filter(owner=user)


# --- RECIPIENT ---

class RecipientListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Recipient
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipients"


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")
    extra_context = {"title": "Добавить получателя", "button_text": "Создать"}

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, OwnerQuerysetMixin, UpdateView):
    model = Recipient
    fields = ["email", "full_name", "comment"]
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")
    extra_context = {"title": "Редактировать получателя", "button_text": "Сохранить"}


class RecipientDeleteView(LoginRequiredMixin, OwnerQuerysetMixin, DeleteView):
    model = Recipient
    template_name = "mailing/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")


# --- MESSAGE ---

class MessageListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")
    extra_context = {"title": "Добавить сообщение", "button_text": "Создать"}

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, OwnerQuerysetMixin, UpdateView):
    model = Message
    fields = ["subject", "body"]
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")
    extra_context = {"title": "Редактировать сообщение", "button_text": "Сохранить"}


class MessageDeleteView(LoginRequiredMixin, OwnerQuerysetMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")


# --- MAILING ---

class MailingListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    fields = ["start_time", "end_time", "message", "recipients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")
    extra_context = {"title": "Добавить рассылку", "button_text": "Создать"}

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, OwnerQuerysetMixin, UpdateView):
    model = Mailing
    fields = ["start_time", "end_time", "message", "recipients"]
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")
    extra_context = {"title": "Редактировать рассылку", "button_text": "Сохранить"}


class MailingDeleteView(LoginRequiredMixin, OwnerQuerysetMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MailingSendView(LoginRequiredMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        if not request.user.is_superuser and not request.user.groups.filter(name="Менеджеры").exists():
            if mailing.owner != request.user:
                messages.error(request, "Вы не можете запускать чужую рассылку.")
                return redirect("mailing:mailing_list")

        success, message = send_mailing(mailing)

        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

        return redirect("mailing:mailing_list")


# --- INDEX ---

class IndexView(View):
    def get(self, request):
        total_mailings = Mailing.objects.count()
        active_mailings = Mailing.objects.filter(
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now(),
            status=Mailing.STATUS_STARTED,
        ).count()
        total_recipients = Recipient.objects.count()

        # Статистика попыток
        total_attempts = Attempt.objects.count()
        success_attempts = Attempt.objects.filter(status=Attempt.STATUS_SUCCESS).count()
        failed_attempts = Attempt.objects.filter(status=Attempt.STATUS_FAILED).count()

        context = {
            "total_mailings": total_mailings,
            "active_mailings": active_mailings,
            "total_recipients": total_recipients,
            "total_attempts": total_attempts,
            "success_attempts": success_attempts,
            "failed_attempts": failed_attempts,
        }
        return render(request, "mailing/index.html", context)