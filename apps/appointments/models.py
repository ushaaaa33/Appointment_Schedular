from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime
from apps.services.models import Service
from django.db.models import Q


class TimeSlot(models.Model):
    """TimeSlot model for managing available booking times."""
    WEEKDAY_CHOICES = (
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    )
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE,related_name='time_slots')
    day_of_week = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_appointments = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service} - {self.day_of_week}"
    


class Appointment(models.Model):
    """Appointment model for managing user bookings."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        help_text='User who booked the appointment'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='appointments',
        help_text='Service for this appointment'
    )
    appointment_date = models.DateField(help_text='Date of the appointment')
    appointment_time = models.TimeField(help_text='Time of the appointment')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current status of the appointment'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes or requirements'
    )
    admin_notes = models.TextField(
        blank=True,
        help_text='Notes from admin (visible to user)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
    
    def __str__(self):
        return f"{self.user.username} - {self.service.name} on {self.appointment_date}"
    
    def clean(self):
        """Validate appointment date and time."""
        
        
        # Check if appointment is in the past
        if self.appointment_date and self.appointment_time:
            appointment_datetime = datetime.combine(
                self.appointment_date,
                self.appointment_time
            )
            if appointment_datetime < datetime.now():
                raise ValidationError('Cannot book appointments in the past.')
        
        # Check if the time slot is available for this service
        if self.service and self.appointment_date and self.appointment_time:
            # Get the day of week for the appointment date (0=Monday, 6=Sunday)
            day_of_week = self.appointment_date.weekday()
            
            # Find matching time slots
            matching_slots = TimeSlot.objects.filter(
                service=self.service,
                day_of_week=day_of_week,
                start_time__lte=self.appointment_time,
                end_time__gt=self.appointment_time,
                is_available=True
            )
            
            if not matching_slots.exists():
                raise ValidationError(
                    f'No available time slot for {self.service.name} on '
                    f'{self.appointment_date.strftime("%A")} at {self.appointment_time.strftime("%I:%M %p")}. '
                    f'Please check available time slots.'
                )
            
            # Check if the slot has reached max appointments
            time_slot = matching_slots.first()
            existing_appointments = Appointment.objects.filter(
                service=self.service,
                appointment_date=self.appointment_date,
                appointment_time=self.appointment_time,
                status__in=['pending', 'approved']
            ).exclude(pk=self.pk if self.pk else None).count()
            
            if existing_appointments >= time_slot.max_appointments:
                raise ValidationError(
                    f'This time slot is fully booked. Maximum {time_slot.max_appointments} '
                    f'appointment(s) allowed.'
            )
    
    @property
    def status_color(self):
        """Return color class based on status."""
        colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary',
            'completed': 'info',
        }
        return colors.get(self.status, 'secondary')