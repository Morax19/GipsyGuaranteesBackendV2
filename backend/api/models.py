from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Test(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Warranty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    purchase_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} ({self.serial_number}) - {self.user.username}"
