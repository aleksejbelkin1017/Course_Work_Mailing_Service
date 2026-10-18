from django.core.mail import send_mail
from django.utils import timezone

from mailing.models import Attempt, Mailing


def send_mailing(mailing: Mailing) -> tuple[bool, str]:
    """
    Отправляет рассылку получателям.
    Возвращает кортеж (успех, сообщение).
    """
    now = timezone.now()

    # 1. Проверка времени
    if now < mailing.start_time:
        return False, f"Рассылка ещё не началась. Начало: {mailing.start_time:%d.%m.%Y %H:%M}"
    if now > mailing.end_time:
        return False, f"Рассылка уже завершена. Окончание: {mailing.end_time:%d.%m.%Y %H:%M}"

    # 2. Проверка наличия получателей
    recipients = mailing.recipients.all()
    if not recipients:
        return False, "У рассылки нет получателей."

    # 3. Отправка писем
    subject = mailing.message.subject
    body = mailing.message.body
    from_email = "noreply@mailing-service.ru"
    success_count = 0
    fail_count = 0

    for recipient in recipients:
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            Attempt.objects.create(
                mailing=mailing,
                status=Attempt.STATUS_SUCCESS,
                server_response="Письмо успешно отправлено",
            )
            success_count += 1
        except Exception as e:
            Attempt.objects.create(
                mailing=mailing,
                status=Attempt.STATUS_FAILED,
                server_response=str(e),
            )
            fail_count += 1

    # 4. Обновляем статус рассылки
    mailing.update_status()

    return True, f"Рассылка завершена. Успешно: {success_count}, Ошибок: {fail_count}."
