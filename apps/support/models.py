from django.db import models


class SupportTicket(models.Model):
    STATUS_CHOICES = (
        ('open', 'Aberto'),
        ('in_progress', 'Em Andamento'),
        ('resolved', 'Resolvido'),
        ('closed', 'Fechado'),
    )

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject}"


class SupportMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey('users.User', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
