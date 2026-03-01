from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime
from apps.services.models import Service
from django.contrib import messages


class Weekday(models.Model):
    # To set multiple days for the appointments
    WEEKDAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    day = models.IntegerField(choices=WEEKDAY_CHOICES, unique=True)

    def __str__(self):
        return dict(self.WEEKDAY_CHOICES)[self.day]


class TimeSlot(models.Model):
    # TimeSlot model for managing available booking times

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='time_slots'
    )
    day_of_week = models.ManyToManyField(
        Weekday,
        related_name='time_slots'
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_appointments = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        days = ", ".join([str(day) for day in self.day_of_week.all()])
        return f"{self.service.name} - {days}"

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

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None

        if not is_new:
            old_status = Appointment.objects.get(pk=self.pk).status
        super().save(*args, **kwargs)

        # Trigger notification only if status changed
        if not is_new and old_status != self.status:
            Notification.objects.create(user=self.user, message=f"Your appointment has been {self.status}.")
    
    def create_status_notification(self):
        messages = {
            'approved': f"Your appointment for {self.service.name} has been approved.",
            'rejected': f"Your appointment for {self.service.name} was rejected.",
            'completed': f"Your appointment for {self.service.name} is completed.",
            'cancelled': f"Your appointment for {self.service.name} was cancelled.",
        }

        message = messages.get(self.status)
        if message:
            Notification.objects.create(user=self.user, message=message)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
    
    def __str__(self):
        return f"{self.user.username} - {self.service.name} on {self.appointment_date}"
    
    def clean(self):
        """Validate appointment date and time."""
        if self.appointment_date:
            appointment_datetime = datetime.combine(
                self.appointment_date,
                self.appointment_time if self.appointment_time else datetime.min.time()
            )
            if appointment_datetime < datetime.now():
                raise ValidationError('Cannot book appointments in the past.')
    
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


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user}"