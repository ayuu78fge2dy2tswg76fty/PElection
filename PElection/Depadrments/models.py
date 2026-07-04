from django.db import models

# Create your models here.

class depadrments_DB(models.Model):
    d_name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
    
    def __str__(self):
        return self.d_name
