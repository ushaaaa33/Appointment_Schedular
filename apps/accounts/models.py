"""
Custom User model with profile picture upload handling.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import os


def validate_image_size(image):
    """Validate that uploaded image is not too large."""
    max_size_mb = 2  # Maximum 2MB for profile pictures
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            f'Image too large. Maximum size is {max_size_mb}MB.'
        )


def profile_picture_path(instance, filename):
    """
    Generate upload path for profile pictures.
    Files will be saved as: media/profiles/user_<id>/<filename>
    """
    ext = filename.split('.')[-1].lower()
    new_filename = f"profile_{instance.username}.{ext}"
    return os.path.join('profiles', new_filename)


class User(AbstractUser):
    """
    Custom User model with role-based authentication
    and profile picture support.
    """

    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        help_text='User role for access control'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Contact phone number'
    )
    profile_picture = models.ImageField(
        upload_to=profile_picture_path,
        blank=True,
        null=True,
        validators=[validate_image_size],
        help_text='Profile picture (max 2MB)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        """Override save to delete old profile picture when updating."""
        if self.pk:
            try:
                old_instance = User.objects.get(pk=self.pk)
                if (old_instance.profile_picture and
                        old_instance.profile_picture != self.profile_picture):
                    if os.path.isfile(old_instance.profile_picture.path):
                        os.remove(old_instance.profile_picture.path)
            except User.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    @property
    def is_admin_user(self):
        """Check if user has admin role."""
        return self.role == 'admin' or self.is_staff or self.is_superuser

    @property
    def is_regular_user(self):
        """Check if user has regular user role."""
        return self.role == 'user'

    @property
    def profile_picture_url(self):
        """
        Return profile picture URL safely.
        Returns None if no picture uploaded.
        """
        if self.profile_picture:
            return self.profile_picture.url
        return None