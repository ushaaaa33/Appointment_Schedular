from django.core.mail import send_mail
from django.conf import settings
from .models import Notification


def create_notification(user, notification_type, title, message, appointment_id=None, send_email=True):
    """
    Create a notification and optionally send email.
    
    Args:
        user: User object
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        appointment_id: Related appointment ID (optional)
        send_email: Whether to send email notification (default: True)
    """
    # Create database notification
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        appointment_id=appointment_id
    )
    
    # Send email notification
    if send_email and user.email:
        try:
            email_subject = f"{settings.SITE_NAME} - {title}"
            email_message = f"""
Hello {user.get_full_name() or user.username},

{message}

You can view your appointment details at:
{settings.SITE_URL}/appointments/detail/{appointment_id}/

Thank you for using {settings.SITE_NAME}!

---
This is an automated message. Please do not reply to this email.
            """
            
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@appointease.com',
                recipient_list=[user.email],
                fail_silently=True,  # Don't crash if email fails
            )
        except Exception as e:
            print(f"Failed to send email to {user.email}: {e}")
    
    return notification


def notify_appointment_approved(appointment):
    """Notify user that their appointment is approved."""
    create_notification(
        user=appointment.user,
        notification_type='appointment_approved',
        title='✅ Appointment Approved',
        message=f'Your appointment for {appointment.service.name} on {appointment.appointment_date.strftime("%B %d, %Y")} at {appointment.appointment_time.strftime("%I:%M %p")} has been approved!',
        appointment_id=appointment.id,
        send_email=True
    )


def notify_appointment_cancelled(appointment):
    """Notify user that their appointment is cancelled."""
    create_notification(
        user=appointment.user,
        notification_type='appointment_cancelled',
        title='❌ Appointment Cancelled',
        message=f'Your appointment for {appointment.service.name} on {appointment.appointment_date.strftime("%B %d, %Y")} has been cancelled.',
        appointment_id=appointment.id,
        send_email=True
    )


def notify_appointment_rejected(appointment):
    """Notify user that their appointment is rejected."""
    create_notification(
        user=appointment.user,
        notification_type='appointment_rejected',
        title='⛔ Appointment Rejected',
        message=f'Your appointment for {appointment.service.name} on {appointment.appointment_date.strftime("%B %d, %Y")} has been rejected. Please contact support.',
        appointment_id=appointment.id,
        send_email=True
    )


def notify_appointment_reminder(appointment):
    """Send reminder notification 1 day before appointment."""
    create_notification(
        user=appointment.user,
        notification_type='appointment_reminder',
        title='⏰ Appointment Reminder',
        message=f'Reminder: You have an appointment for {appointment.service.name} tomorrow at {appointment.appointment_time.strftime("%I:%M %p")}. Please be on time!',
        appointment_id=appointment.id,
        send_email=True
    )