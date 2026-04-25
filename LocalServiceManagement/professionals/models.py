from django.db import models
from services.models import Service

class Professional(models.Model):

    name = models.CharField(max_length=100)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    experience = models.IntegerField()
    rating = models.FloatField(default=0)
    jobs_completed = models.IntegerField(default=0)
    photo = models.ImageField(upload_to="professionals/", blank=True)

    def __str__(self):
        return self.name