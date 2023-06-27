from django.db import models
from users.models import Account


def public_chat_images_path(self, filename):
    return f'Chat_images/public_chat/{str(self.id)}'

class Images(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=public_chat_images_path, blank=True, null=True)