from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime
from .models import Appointment, TimeSlot
from apps.services.models import Service


class AppointmentForm(forms.ModelForm):
    """Form for creating appointments."""
    
    class Meta:
        model = Appointment
        fields = ('service', 'appointment_date', 'appointment_time', 'notes')
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control form-select'}),
            'appointment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': datetime.now().date().isoformat(),
            }),
            'appointment_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requirements or notes...',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['notes'].required = False
    
    def clean_appointment_date(self):
        """Validate appointment date."""
        date = self.cleaned_data.get('appointment_date')
        if date and date < datetime.now().date():
            raise ValidationError('Cannot book appointments for past dates.')
        return date
    
    def clean(self):
        """Validate appointment datetime and check TimeSlot availability."""
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        date = cleaned_data.get('appointment_date')
        time = cleaned_data.get('appointment_time')

        # Existing check for past datetime
        if date and time:
            appointment_datetime = datetime.combine(date, time)
            if appointment_datetime < datetime.now():
                raise ValidationError('Cannot book appointments in the past.')

        # TimeSlot validation
        if service and date and time:
            weekday = date.weekday()  # Monday=0, Sunday=6

            # Get all available TimeSlots for this service on this day
            slots = TimeSlot.objects.filter(
                service=service,
                day_of_week__day=weekday,
                is_available=True
            )

            # Check if appointment time fits in any slot
            valid_slot = None
            for slot in slots:
                if slot.start_time <= time < slot.end_time:
                    # Check if max appointments reached
                    booked_count = Appointment.objects.filter(
                        service=service,
                        appointment_date=date,
                        appointment_time=time,
                        status__in=['pending', 'approved']
                    ).count()
                    if booked_count < slot.max_appointments:
                        valid_slot = slot
                        break

            if not valid_slot:
                raise ValidationError(
                    f"No available time slot for {service.name} on {date.strftime('%A')} at {time.strftime('%I:%M %p')}."
                )

        return cleaned_data