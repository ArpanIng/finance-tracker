from celery import shared_task
from django.contrib.auth import get_user_model

from .consumers import notify_user

User = get_user_model()


@shared_task
def send_daily_notifications():
    users = User.objects.all()
    for user in users:
        message = "Have you recorded your transactions today?"
        notify_user(user_id=user.id, message=message)
