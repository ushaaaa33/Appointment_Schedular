from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import AppointmentForm
from .models import Appointment


@login_required
def create_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            messages.success(request, "Appointment booked successfully!")
            return redirect("my_appointments")
    else:
        form = AppointmentForm()

    return render(request, "appointments/create.html", {"form": form})

@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, "appointments/my_appointments.html",{"appointments": appointments})

@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, user=request.user)

    if appointment.status == "pending":
        appointment.status = "cancelled"
        appointment.save()
        messages.success(request, "Appointment cancelled successfully.")
    else:
        messages.error(request, "You cannot cancel this appointment.")

    return redirect("my_appointments")

@staff_member_required
def update_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    status = request.POST.get("status")

    if status in ["pending", "confirmed", "cancelled"]:
        appointment.status = status
        appointment.save()

    return redirect("manage_appointments")

@staff_member_required
def manage_appointments(request):
    appointments = Appointment.objects.all().order_by("-appointment_date")
    return render(request, "appointments/manage_appointments.html", {
        "appointments": appointments
    })

