from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Post


@shared_task
def create_post(user_id, title, content, scheduled_time):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    if scheduled_time > timezone.now():
        Post.objects.create(
            user=user,
            title=title,
            content=content,
            created_at=scheduled_time
        )
        return f"Post '{title}' scheduled for {scheduled_time}"
    else:
        return "Scheduled time should be in the future"
