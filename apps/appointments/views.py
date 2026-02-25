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
from .models import Appointment
from .forms import AppointmentForm
from django.contrib.auth.mixins import LoginRequiredMixin


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


class AppointmentListView(LoginRequiredMixin, ListView):
    """View for listing user's appointments with filtering."""
    
    model = Appointment
    template_name = 'appointments/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 10
    
    def get_queryset(self):
        if self.request.user.is_admin_user:
            queryset = Appointment.objects.all()
        else:
            queryset = Appointment.objects.filter(user=self.request.user)
        
        # Filter by status from URL parameter
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-appointment_date', '-appointment_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_status'] = self.request.GET.get('status', '')
        return context


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