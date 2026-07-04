from django.core.exceptions import ValidationError
from django.db import models

from Musharax.models import musharax_DB
from Depadrments.models import depadrments_DB
from voiteID.models import ID_DB


class codbixiye_DB(models.Model):
    gender_choice =[
        ("lab", "Lab"),
        ("dhadig", "DHadig")
    ]

    c_id = models.OneToOneField(ID_DB,on_delete=models.CASCADE,related_name="codbixiye",limit_choices_to={'_is_used': False})

    c_department = models.ForeignKey(depadrments_DB,on_delete=models.CASCADE,related_name="voters")

    c_musharax = models.ForeignKey(musharax_DB,on_delete=models.CASCADE,related_name="codbixiye")
    c_gender = models.CharField(max_length=20, choices=gender_choice,default='')

    class Meta:
        verbose_name = "Codbixiye"
        verbose_name_plural = "Codbixiyeyaal"
        ordering = ["c_id"]


    def clean(self):
        super().clean()

        if self.c_id._is_used:
            raise ValidationError({
                "c_id": "ID horay aya lo isticmalay."
            })
        

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)

      
        self.c_id._is_used = True
        self.c_id.save(update_fields=["_is_used"])

    def __str__(self):
        return str(self.c_id)