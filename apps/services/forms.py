"""
Forms for Service model with image upload validation.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Service


class ServiceForm(forms.ModelForm):
    """Form for creating and editing services with image upload."""

    class Meta:
        model = Service
        fields = (
            'name',
            'description',
            'category',
            'duration_minutes',
            'price',
            'image',
            'is_active'
        )
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. General Consultation'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the service in detail...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control form-select'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'max': 480,
                'placeholder': '30'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/webp'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_image(self):
        """Validate image file type and size."""
        image = self.cleaned_data.get('image')
        if image:
            # Check file extension
            valid_extensions = ['jpg', 'jpeg', 'png', 'webp']
            ext = image.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise ValidationError(
                    f'Unsupported file type: .{ext}. '
                    f'Please upload JPG, PNG, or WEBP images only.'
                )
            # Check file size (5MB max)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError(
                    'Image file too large. Maximum size is 5MB. '
                    f'Your file is {image.size / (1024 * 1024):.1f}MB.'
                )
        return image