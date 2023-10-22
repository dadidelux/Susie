from django.db import models

from django.db import models
from django.contrib.auth.models import User
from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD


class ChatSession(models.Model):
    # Your ChatSession fields
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ChatHistory(models.Model):

    class Meta:
        verbose_name = ("Chat historie")

    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_prompt = models.TextField()
    system_response = models.JSONField(null=True)
    system_response_2 = MarkdownField(rendered_field='text_rendered', use_editor=False, validator=VALIDATOR_STANDARD)
    system_response_rendered = RenderedMarkdownField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"
