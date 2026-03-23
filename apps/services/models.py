"""
Service model with full image upload handling.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import os
from django.contrib.auth.models import User
from django.conf import settings


def validate_image_size(image):
    """Validate that uploaded image is not too large."""
    max_size_mb = 5  # Maximum 5MB
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            f'Image file too large. Maximum size is {max_size_mb}MB. '
            f'Your file is {image.size / (1024 * 1024):.1f}MB.'
        )


def service_image_path(instance, filename):
    """
    Generate upload path for service images.
    Files will be saved as: media/services/service_<id>/<filename>
    """
    ext = filename.split('.')[-1].lower()
    # Clean the service name for use in filename
    clean_name = instance.name.lower().replace(' ', '_')
    new_filename = f"{clean_name}_image.{ext}"
    return os.path.join('services', new_filename)


class Service(models.Model):
    """
    Service model representing different types of services offered.
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    doctor = models.ForeignKey(
        "Doctor",
        on_delete=models.CASCADE,
        related_name="services",
        null=True,
        blank=True
    )
   

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

    name = models.CharField(
        max_length=200,
        help_text='Name of the service'
    )
    description = models.TextField(
        help_text='Detailed description of the service'
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other',
        help_text='Service category'
    )
    duration_minutes = models.PositiveIntegerField(
        default=30,
        help_text='Duration of the service in minutes'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Price of the service'
    )
    image = models.ImageField(
        upload_to=service_image_path,  # Uses our custom path function
        blank=True,
        null=True,
        validators=[validate_image_size],
        help_text='Service image (max 5MB, JPG/PNG/WEBP)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this service is currently available'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return f"{self.name} (${self.price})"

    def save(self, *args, **kwargs):
        """Override save to delete old image when updating."""
        # If updating and image has changed, delete the old one
        if self.pk:
            try:
                old_instance = Service.objects.get(pk=self.pk)
                if old_instance.image and old_instance.image != self.image:
                    # Delete old image file from disk
                    if os.path.isfile(old_instance.image.path):
                        os.remove(old_instance.image.path)
            except Service.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to also remove image file."""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    @property
    def duration_display(self):
        """Return formatted duration string."""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"

    @property
    def image_url(self):
        """
        Return image URL or None.
        Use this in templates instead of service.image.url
        to avoid errors when no image is uploaded.
        """
        if self.image:
            return self.image.url
        return None

    @property
    def category_icon(self):
        """Return emoji icon based on category."""
        icons = {
            'consultation': '🩺',
            'diagnostic': '🔬',
            'dental': '🦷',
            'therapy': '💪',
            'mental_health': '🧠',
            'specialist': '👨‍⚕️',
            'wellness': '🥗',
            'emergency': '🚨',
            'other': '🎯',
        }
        return icons.get(self.category, '🎯')
    
#Doctor Profile

class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=255)
    bio = models.TextField(blank=True)

    profile_image = models.ImageField(
        upload_to='doctors/',
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"
    

class Education(models.Model):
    doctor = models.ForeignKey(Doctor, related_name="educations", on_delete=models.CASCADE)
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    year = models.IntegerField()


class Experience(models.Model):
    doctor = models.ForeignKey(Doctor, related_name="experiences", on_delete=models.CASCADE)
    position = models.CharField(max_length=200)
    hospital = models.CharField(max_length=200)
    start_year = models.IntegerField()
    end_year = models.IntegerField(blank=True, null=True)


class Language(models.Model):
    doctor = models.ForeignKey(Doctor, related_name="languages", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)