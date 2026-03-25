"""
Admin configuration for Service model with image preview.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Service, Doctor, Education, Experience, Language


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin interface for Service model with image preview."""

    list_display = (
        'image_preview',
        'name',
        'doctor',
        'category',
        'price',
        'duration_minutes',
        'is_active',
        'created_at'
    )
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'description', 'doctor_user_first_name')
    list_editable = ('is_active',)
    ordering = ('category', 'name')
    readonly_fields = ('created_at', 'updated_at', 'image_preview_large')

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'doctor',
                'description',
                'category',
            ),
        }),
        ('Service Image', {
            'fields': ('image', 'image_preview_large'),
            'description': 'Upload a service image (JPG, PNG, WEBP - max 5MB)',
        }),
        ('Pricing & Duration', {
            'fields': ('duration_minutes', 'price', 'is_active'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def image_preview(self, obj):
        """Show small image thumbnail in list view."""
        if obj.image:
            return format_html(
                '<img src="{}" style="width:50px; height:50px; '
                'object-fit:cover; border-radius:8px;" />',
                obj.image.url
            )
        # Use mark_safe for static HTML without placeholders
        return mark_safe(
            '<div style="width:50px; height:50px; background:#e2e8f0; '
            'border-radius:8px; display:flex; align-items:center; '
            'justify-content:center; font-size:1.5rem;">'
            f'{obj.category_icon}'
            '</div>'
        )
    image_preview.short_description = 'Image'

    def image_preview_large(self, obj):
        """Show larger image preview in detail view."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px; max-height:200px; '
                'object-fit:cover; border-radius:12px; '
                'box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />',
                obj.image.url
            )
        # Use mark_safe for static HTML
        return mark_safe('<p style="color:#64748b;">No image uploaded yet.</p>')
    
    image_preview_large.short_description = 'Current Image Preview'

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'degree', 'institution', 'year')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'position', 'hospital', 'start_year', 'end_year')


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'name')
    