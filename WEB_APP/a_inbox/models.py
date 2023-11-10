import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timesince import timesince
from django.conf import settings
from cryptography.fernet import Fernet


class InboxMessage(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    conversation = models.ForeignKey(
        "Conversation", on_delete=models.CASCADE, related_name="messages"
    )
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self) -> str:
        time_since = timesince(self.created, timezone.now())
        return f"[{self.sender.username} : {time_since} ago]"

    def decrypted_body(self) -> str:
        f = Fernet(settings.ENCRYPT_KEY)
        original_message = f.decrypt(self.body)
        decoded_message = original_message.decode()
        return decoded_message


class Conversation(models.Model):
    id = models.CharField(
        max_length=100,
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False,
    )
    participants = models.ManyToManyField(User, related_name="conversations")
    lastmessage_created = models.DateTimeField(default=timezone.now)
    is_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ["-lastmessage_created"]

    def __str__(self) -> str:
        users = ", ".join([user.username for user in self.participants.all()])
        return f"[{users}]"
