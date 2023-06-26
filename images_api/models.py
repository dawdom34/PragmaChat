from django.db import models
from users.models import Account


def public_chat_images_path(self):
    return f'Chat_images/public_chat/{str(self.pk)}'

class Images(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=public_chat_images_path)