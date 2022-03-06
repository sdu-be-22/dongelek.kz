from django.db import models

# Create your models here.
class Person(models.Model):
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=10)
    
    def __str__(self) -> str:
        return f"{{self.first_name}} {{self.last_name}}"