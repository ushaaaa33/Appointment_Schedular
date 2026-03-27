"""
Views for appointment management.
Includes CRUD operations and status management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from .models import Appointment, Payment
from .forms import AppointmentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
import requests
from django.db import transaction
from django.utils import timezone



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

@login_required
def khalti_payment(request, appointment_id):
    
    # 1. Get appointment
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        user=request.user
    )

    # 2. Prevent duplicate payments
    if hasattr(appointment, "payment") and appointment.payment.status == Payment.Status.SUCCESS:
        messages.info(request, "This appointment is already paid.")
        return redirect("user_dashboard")

    # 3. Create or get payment
    payment, created = Payment.objects.get_or_create(
        appointment=appointment,
        defaults={
            "amount": appointment.service.price,  
            "status": Payment.Status.PENDING,
        }
    )

    # Prevent re-initiation if already processed
    if not created and payment.status != Payment.Status.PENDING:
        messages.warning(request, "Payment already processed.")
        return redirect("user_dashboard")

    # 4. Convert amount
    amount_paisa = int(payment.amount * 100)

    # 5. Khalti payload
    payload = {
        "return_url": settings.SITE_URL + reverse("khalti_payment_response"),
        "website_url": settings.SITE_URL,
        "amount": amount_paisa,
        "purchase_order_id": str(appointment.id),
        "purchase_order_name": f"Appointment-{appointment.id}",
        "customer_info": {
            "name": request.user.get_full_name() or request.user.email,
            "email": request.user.email,
        },
    }

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            "https://dev.khalti.com/api/v2/epayment/initiate/",
            json=payload,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

    except requests.RequestException:
        messages.error(request, "Payment service unavailable.")
        return redirect("user_dashboard")

    pidx = data.get("pidx")
    payment_url = data.get("payment_url")

    if not pidx or not payment_url:
        messages.error(request, "Invalid payment response.")
        return redirect("user_dashboard")

    payment.pidx = pidx
    payment.save(update_fields=["pidx"])

    return redirect(payment_url)


@login_required
def khalti_payment_response(request):
    print("🔥 Khalti response view hit")
    
    pidx = request.GET.get("pidx")
    print("PIDX:", pidx)
    
    if not pidx:
        messages.error(request, "Invalid payment response.")
        return redirect("user_dashboard")

    try:
        payment = Payment.objects.select_related("appointment").get(pidx=pidx)

    except Payment.DoesNotExist:
        messages.error(request, "Payment record not found.")
        return redirect("user_dashboard")

    # Prevent duplicate processing
    if payment.status == Payment.Status.SUCCESS:
        messages.info(request, "Payment already verified.")
        return redirect("user_dashboard")

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            "https://dev.khalti.com/api/v2/epayment/lookup/",
            json={"pidx": pidx},
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

    except requests.RequestException:
        messages.error(request, "Payment verification failed.")
        return redirect("user_dashboard")

    # Payment not completed
    if data.get("status") != "Completed":
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status"])

        messages.error(request, "Payment failed or cancelled.")
        return redirect("user_dashboard")

    # Validate amount
    total_amount = int(data.get("total_amount", 0))
    expected_amount = int(payment.amount * 100)

    if total_amount != expected_amount:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status"])

        messages.error(request, "Payment amount mismatch.")
        return redirect("user_dashboard")

    transaction_id = data.get("transaction_id")

    # Finalize
    try:
        with transaction.atomic():

            payment.transaction_id = transaction_id
            payment.status = Payment.Status.SUCCESS
            payment.paid_at = timezone.now()
            payment.save(update_fields=["transaction_id", "status", "paid_at"])

            # 🔥 IMPORTANT: Update appointment
            appointment = payment.appointment
            appointment.status = "approved"  # or confirmed
            appointment.save(update_fields=["status"])

    except Exception:
        messages.error(request, "Something went wrong.")
        return redirect("user_dashboard")

    # ✅ THIS IS YOUR TASK REQUIREMENT
    messages.success(request, "Payment successful. Appointment confirmed.")
    print("Payment object:", payment)

    return redirect("user_dashboard")