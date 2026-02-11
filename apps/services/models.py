from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Service(models.Model):
    """Service model representing different types of services offered."""
    
    name = models.CharField(max_length=200, help_text='Name of the service')
    description = models.TextField(help_text='Detailed description of the service')
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
        upload_to='services/',
        blank=True,
        null=True,
        help_text='Service image'
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