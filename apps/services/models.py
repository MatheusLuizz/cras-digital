from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(help_text="Duração padrão do serviço em minutos")
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name
