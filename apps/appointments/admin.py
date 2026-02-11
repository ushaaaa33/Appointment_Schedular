from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin interface for Appointment model."""
    
    list_display = ('user', 'service', 'appointment_date', 'appointment_time', 'status', 'created_at')
    list_filter = ('status', 'appointment_date', 'service', 'created_at')
    search_fields = ('user__username', 'user__email', 'service__name', 'notes')
    list_editable = ('status',)
    date_hierarchy = 'appointment_date'
    ordering = ('-appointment_date', '-appointment_time')
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('user', 'service', 'appointment_date', 'appointment_time'),
        }),
        ('Status', {
            'fields': ('status',),
        }),
        ('Notes', {
            'fields': ('notes', 'admin_notes'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['approve_appointments', 'reject_appointments']
    
    def approve_appointments(self, request, queryset):
        """Bulk action to approve appointments."""
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} appointment(s) approved successfully.')
    approve_appointments.short_description = 'Approve selected appointments'
    
    def reject_appointments(self, request, queryset):
        """Bulk action to reject appointments."""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} appointment(s) rejected.')
    reject_appointments.short_description = 'Reject selected appointments'