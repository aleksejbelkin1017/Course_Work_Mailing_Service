from django.views.generic import ListView

from mailing.models import Recipient


class RecipientListView(ListView):
    """Страница со списком всех получателей."""
    model = Recipient
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipients"
