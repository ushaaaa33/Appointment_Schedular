from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification


@login_required
def notification_list(request):
    """Display all notifications for logged-in user."""
    notifications = request.user.notifications.all()
    
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count()
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def mark_as_read(request, notification_id):
    """Mark a notification as read."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    # Redirect to appointment if exists
    if notification.appointment_id:
        return redirect('appointment_detail', pk=notification.appointment_id)
    
    return redirect('notification_list')


@login_required
def mark_all_as_read(request):
    """Mark all notifications as read."""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notification_list')