from django.db import models


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
