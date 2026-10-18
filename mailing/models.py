from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

class Recipient(models.Model):
    """Модель получателя рассылки."""
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Введите email получателя",
    )
    full_name = models.CharField(
        max_length=255,
        verbose_name="Ф. И. О.",
        help_text="Введите ФИО получателя",
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий",
        help_text="Необязательный комментарий",
    )

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылки"
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} <{self.email}>"


class Message(models.Model):
    """Модель сообщения для рассылки."""
    subject = models.CharField(
        max_length=255,
        verbose_name="Тема письма",
        help_text="Введите тему письма",
    )
    body = models.TextField(
        verbose_name="Тело письма",
        help_text="Введите текст письма",
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["subject"]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """Модель рассылки."""

    STATUS_CREATED = "created"
    STATUS_STARTED = "started"
    STATUS_FINISHED = "finished"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_STARTED, "Запущена"),
        (STATUS_FINISHED, "Завершена"),
    ]

    start_time = models.DateTimeField(
        verbose_name="Дата и время начала отправки",
        help_text="С какого момента рассылка может быть запущена",
    )
    end_time = models.DateTimeField(
        verbose_name="Дата и время окончания отправки",
        help_text="До какого момента разрешено выполнять отправку",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name="Статус",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="mailings",
        verbose_name="Сообщение",
    )
    recipients = models.ManyToManyField(
        Recipient,
        related_name="mailings",
        verbose_name="Получатели",
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-start_time"]

    def __str__(self):
        return f"Рассылка #{self.pk} — {self.message.subject}"

    def clean(self):
        """Валидация: start_time не в прошлом, start_time < end_time."""
        if self.start_time and self.end_time:
            if self.start_time < timezone.now():
                raise ValidationError({
                    "start_time": "Дата начала не может быть в прошлом."
                })
            if self.start_time >= self.end_time:
                raise ValidationError({
                    "end_time": "Дата окончания должна быть позже даты начала."
                })

    def update_status(self, save: bool = True):
        """
        Пересчитывает статус на основе текущего времени.
        Если статус изменился — сохраняет в БД.
        """
        now = timezone.now()

        if now < self.start_time:
            new_status = self.STATUS_CREATED
        elif self.start_time <= now <= self.end_time:
            new_status = self.STATUS_STARTED
        else:
            new_status = self.STATUS_FINISHED

        if self.status != new_status:
            self.status = new_status
            if save:
                super().save(update_fields=["status"])

        return self.status


class Attempt(models.Model):
    """Модель попытки отправки сообщения."""

    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Успешно"),
        (STATUS_FAILED, "Не успешно"),
    ]

    attempt_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время попытки",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name="Статус",
    )
    server_response = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ответ почтового сервера",
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка",
    )

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
        ordering = ["-attempt_time"]

    def __str__(self):
        return f"Попытка #{self.pk} — {self.get_status_display()} ({self.mailing})"
