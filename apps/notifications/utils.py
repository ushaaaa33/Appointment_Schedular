"""
Notification helper functions.
"""
from .models import Notification


def create_notification(user, notification_type, title, message, appointment_id=None):
    """
    Create a notification for a user.
    
    Args:
        user: User object
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        appointment_id: Related appointment ID (optional)
    """
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        appointment_id=appointment_id
    )


def notify_appointment_approved(appointment):
    """Notify user that their appointment is approved."""
    create_notification(
        user=appointment.user,
        notification_type='appointment_approved',
        title='✅ Appointment Approved',
        message=f'Your appointment for {appointment.service.name} on {appointment.appointment_date.strftime("%B %d, %Y")} at {appointment.appointment_time.strftime("%I:%M %p")} has been approved!',
        appointment_id=appointment.id
    )


def notify_appointment_cancelled(appointment):
    """Notify user that their appointment is cancelled."""
    create_notification(
        user=appointment.user,
        notification_type='appointment_cancelled',
        title='❌ Appointment Cancelled',
        message=f'Your appointment for {appointment.service.name} on {appointment.appointment_date.strftime("%B %d, %Y")} has been cancelled.',
        appointment_id=appointment.id
    )


def notify_appointment_rejected(appointment):
    """Notify user that their appointment is rejected."""
    create_notification(
        user=appointment.user,
        notification_type='appointment_rejected',
        title='⛔ Appointment Rejected',
        message=f'Your appointment for {appointment.service.name} on {appointment.appointment_date.strftime("%B %d, %Y")} has been rejected. Please contact support.',
        appointment_id=appointment.id
    )