from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime
from .models import Appointment
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
        """Validate appointment datetime."""
        cleaned_data = super().clean()
        date = cleaned_data.get('appointment_date')
        time = cleaned_data.get('appointment_time')
        
        if date and time:
            appointment_datetime = datetime.combine(date, time)
            if appointment_datetime < datetime.now():
                raise ValidationError('Cannot book appointments in the past.')
        
        return cleaned_data