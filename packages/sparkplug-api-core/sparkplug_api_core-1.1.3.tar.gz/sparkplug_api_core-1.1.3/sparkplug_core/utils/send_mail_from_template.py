from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_mail_from_template(
    *,
    recipient: str,
    subject: str,
    template_name: str,
    context: dict[str, str],
) -> None:
    # Generate the email body from a Django template.
    message = render_to_string(
        template_name=template_name,
        context=context,
    )

    # Send the email.
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
    )
