"""
Service model with full image upload handling.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import os
from django.conf import settings


def validate_image_size(image):
    """Validate that uploaded image is not too large."""
    max_size_mb = 5
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            f'Image file too large. Maximum size is {max_size_mb}MB. '
            f'Your file is {image.size / (1024 * 1024):.1f}MB.'
        )


def service_image_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    clean_name = instance.name.lower().replace(' ', '_')
    new_filename = f"{clean_name}_image.{ext}"
    return os.path.join('services', new_filename)


class Service(models.Model):
    CATEGORY_CHOICES = (
        ('consultation', 'Consultation'),
        ('diagnostic', 'Diagnostic & Testing'),
        ('dental', 'Dental Care'),
        ('therapy', 'Therapy & Rehabilitation'),
        ('mental_health', 'Mental Health'),
        ('specialist', 'Specialist Consultation'),
        ('wellness', 'Wellness & Nutrition'),
        ('emergency', 'Emergency Services'),
        ('other', 'Other Services'),
    )

    name = models.CharField(max_length=200, help_text='Name of the service')
    description = models.TextField(help_text='Detailed description')
    doctor = models.ForeignKey(
        "Doctor",
        on_delete=models.CASCADE,
        related_name="services",
        null=True,
        blank=True
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    duration_minutes = models.PositiveIntegerField(default=30)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    image = models.ImageField(
        upload_to=service_image_path,
        blank=True,
        null=True,
        validators=[validate_image_size]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Rs. {self.price})"

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_instance = Service.objects.get(pk=self.pk)
                if old_instance.image and old_instance.image != self.image:
                    if os.path.isfile(old_instance.image.path):
                        os.remove(old_instance.image.path)
            except Service.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)

    @property
    def duration_display(self):
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours and minutes:
            return f"{hours}h {minutes}m"
        elif hours:
            return f"{hours}h"
        return f"{minutes}m"

    @property
    def image_url(self):
        return self.image.url if self.image else None

    @property
    def category_icon(self):
        return {
            'consultation': '🩺',
            'diagnostic': '🔬',
            'dental': '🦷',
            'therapy': '💪',
            'mental_health': '🧠',
            'specialist': '👨‍⚕️',
            'wellness': '🥗',
            'emergency': '🚨',
            'other': '🎯',
        }.get(self.category, '🎯')


# ---------------- DOCTOR MODELS ---------------- #

class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='doctors/', blank=True, null=True)

    def __str__(self):
        full_name = self.user.get_full_name()
        return f"Dr. {full_name}" if full_name else f"Dr. {self.user.username}"


class Education(models.Model):
    doctor = models.ForeignKey(Doctor, related_name="educations", on_delete=models.CASCADE)
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    year = models.IntegerField()

    def __str__(self):
        return f"{self.degree} - {self.doctor}"


class Experience(models.Model):
    doctor = models.ForeignKey(Doctor, related_name="experiences", on_delete=models.CASCADE)
    position = models.CharField(max_length=200)
    hospital = models.CharField(max_length=200)
    start_year = models.IntegerField()
    end_year = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.position} at {self.hospital} ({self.doctor})"


class Language(models.Model):
    doctor = models.ForeignKey(Doctor, related_name="languages", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.doctor})"