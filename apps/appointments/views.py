"""
Views for appointment management.
Includes CRUD operations and status management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from .models import Appointment, Service, TimeSlot
from .forms import AppointmentForm
from datetime import datetime


@method_decorator(login_required, name='dispatch')
class AppointmentCreateView(CreateView):
    """View for creating new appointments."""
    
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    success_url = reverse_lazy('user_dashboard')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 'pending'
        messages.success(self.request, 'Appointment booked successfully! Waiting for approval.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class AppointmentListView(ListView):
    """View for listing user's appointments."""
    
    model = Appointment
    template_name = 'appointments/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 10
    
    def get_queryset(self):
        if self.request.user.is_admin_user:
            return Appointment.objects.all().order_by('-created_at')
        return Appointment.objects.filter(user=self.request.user).order_by('-created_at')


@method_decorator(login_required, name='dispatch')
class AppointmentDetailView(DetailView):
    """View for viewing appointment details."""
    
    model = Appointment
    template_name = 'appointments/appointment_detail.html'
    context_object_name = 'appointment'
    
    def get_queryset(self):
        if self.request.user.is_admin_user:
            return Appointment.objects.all()
        return Appointment.objects.filter(user=self.request.user)


@method_decorator(login_required, name='dispatch')
class AppointmentUpdateView(UpdateView):
    """View for updating appointments (users can only update pending appointments)."""
    
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    success_url = reverse_lazy('appointment_list')
    
    def get_queryset(self):
        # Users can only update their own pending appointments
        if self.request.user.is_admin_user:
            return Appointment.objects.all()
        return Appointment.objects.filter(user=self.request.user, status='pending')
    
    def form_valid(self, form):
        messages.success(self.request, 'Appointment updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class AppointmentDeleteView(DeleteView):
    """View for cancelling/deleting appointments."""
    
    model = Appointment
    template_name = 'appointments/appointment_confirm_delete.html'
    success_url = reverse_lazy('appointment_list')
    
    def get_queryset(self):
        if self.request.user.is_admin_user:
            return Appointment.objects.all()
        return Appointment.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Appointment cancelled successfully.')
        return super().delete(request, *args, **kwargs)


@login_required
def appointment_approve(request, pk):
    """Quick approve appointment (admin only)."""
    
    if not request.user.is_admin_user:
        messages.error(request, 'Permission denied.')
        return redirect('user_dashboard')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'approved'
    appointment.save()
    
    messages.success(request, 'Appointment approved successfully!')
    return redirect('admin_dashboard')


@login_required
def appointment_reject(request, pk):
    """Quick reject appointment (admin only)."""
    
    if not request.user.is_admin_user:
        messages.error(request, 'Permission denied.')
        return redirect('user_dashboard')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'rejected'
    appointment.save()
    
    messages.success(request, 'Appointment rejected.')
    return redirect('admin_dashboard')

def get_available_time_slots(request, service_id):
    """
    Get available time slots for a specific service and date.
    Returns JSON response with available slots.
    """
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({'error': 'Date parameter is required'}, status=400)
    
    try:
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
    
    # Check if date is in the past
    if appointment_date < datetime.now().date():
        return JsonResponse({'available_slots': []})
    
    # Get day of week (0=Monday, 6=Sunday)
    day_of_week = appointment_date.weekday()
    
    # Get all time slots for this service on this day
    time_slots = TimeSlot.objects.filter(
        service=service,
        day_of_week=day_of_week,
        is_available=True
    ).order_by('start_time')
    
    available_slots = []
    
    for slot in time_slots:
        # Count existing appointments for this slot
        existing_appointments = Appointment.objects.filter(
            service=service,
            appointment_date=appointment_date,
            appointment_time=slot.start_time,
            status__in=['pending', 'approved']
        ).count()
        
        # Calculate available capacity
        available_capacity = slot.max_appointments - existing_appointments
        
        if available_capacity > 0:
            available_slots.append({
                'id': slot.id,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'display_time': slot.start_time.strftime('%I:%M %p'),
                'available_capacity': available_capacity,
                'max_appointments': slot.max_appointments
            })
    
    return JsonResponse({
        'service': service.name,
        'date': date_str,
        'day_of_week': appointment_date.strftime('%A'),
        'available_slots': available_slots
    })


def book_appointment_view(request):
    """
    Display the appointment booking form with available services.
    """
    services = Service.objects.filter(is_active=True)
    context = {
        'services': services
    }
    return render(request, 'appointments/book_appointment.html', context )
