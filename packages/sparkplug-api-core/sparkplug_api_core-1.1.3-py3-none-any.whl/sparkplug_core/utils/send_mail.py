from django.conf import settings
from django.core.mail import send_mail as django_send_mail


def send_mail(
    *,
    recipient: str,
    subject: str,
    message: str,
) -> None:
    # Send the email.
    django_send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
    )
