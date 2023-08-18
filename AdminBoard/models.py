from django.db import models

class PromotionalEmail(models.Model):
    recipients = models.TextField() 
    subject = models.CharField(max_length=200)
    content = models.TextField() 
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.subject