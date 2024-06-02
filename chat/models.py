from django.db import models
from django.contrib.auth.models import User


class Thread(models.Model):
    participant1 = models.ForeignKey(User, related_name='threads_participant1', on_delete=models.CASCADE)
    participant2 = models.ForeignKey(User, related_name='threads_participant2', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Thread between {self.participant1.username} and {self.participant2.username}'


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, related_name='messages', on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Message from {self.sender.username} in thread {self.thread.id}'