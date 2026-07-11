import os
from PIL import Image

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models
from Depadrments.models import depadrments_DB


def validate_image_size(image):
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError("Image size must not exceed 5MB.")


def validate_image_content(image):
    try:
        img = Image.open(image)
        img.verify()
    except Exception:
        raise ValidationError("Uploaded file is not a valid image.")


class musharax_DB(models.Model):
    gender_choice = [
        ("lab", "Lab"),
        ("dhadig", "DHadig")
    ]

    m_name = models.CharField(max_length=100,validators=[RegexValidator(regex=r'^[A-Za-zÀ-ÿ\s]+$',message="gali magac saxa ah isticmal xarfo.")],help_text="gali magaca musharaxa.")

    m_email = models.EmailField(unique=True,help_text="gali emailka musharaxa.")

    m_joined = models.DateTimeField(auto_now_add=True)

    m_image = models.ImageField(upload_to="static/musharax_images/",validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),validate_image_size,validate_image_content,])
    
    m_depadrments = models.ForeignKey(depadrments_DB, on_delete=models.CASCADE)

    m_gender = models.CharField(max_length=20, choices=gender_choice, default='')

    m_username = models.CharField(max_length=100, unique=True, help_text="Gali musharax username.",null=True,blank=True)
    
    m_if_allowed= models.BooleanField(default=False,help_text="Ma  Tartami Kara musharaxa.")


    class Meta:
        verbose_name = "Musharax"
        verbose_name_plural = "Musharaxiin"

    def clean(self):
        super().clean()

        if self.m_name:
            self.m_name = self.m_name.strip().title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.m_name