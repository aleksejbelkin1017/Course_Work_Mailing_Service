from django.contrib import admin

from mailing.models import Attempt, Mailing, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name")
    search_fields = ("email", "full_name")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "subject")
    search_fields = ("subject", "body")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "subject_display", "status", "start_time", "end_time")
    list_filter = ("status",)
    search_fields = ("message__subject",)

    def subject_display(self, obj):
        return obj.message.subject
    subject_display.short_description = "Тема сообщения"


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "mailing", "status", "attempt_time")
    list_filter = ("status",)
