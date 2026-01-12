from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True)
def send_confirmation_email(self, to_email: str, username: str):
    """Send account confirmation email asynchronously.

    This is a simple example. In production you might send an HTML
    template, include a verification link with signed token, etc.
    """
    subject = f"Welcome to Social Media, {username}!"
    message = (
        f"Hi {username},\n\n"
        "Thanks for registering. Please confirm your email to complete registration.\n\n"
        "If you did not register, please ignore this message.\n"
    )

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com')

    # send_mail returns number of successfully delivered messages (0/1)
    try:
        result = send_mail(subject, message, from_email, [to_email], fail_silently=False)
        return {'sent': bool(result)}
    except Exception as e:
        # Let Celery record the exception and return failure information
        raise self.retry(exc=e, countdown=60, max_retries=3)
