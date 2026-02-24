"""
Views for user authentication and profile management.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import (
    login,
    logout,
    authenticate,
    update_session_auth_hash
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy

from django.contrib.auth.forms import PasswordChangeForm

from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm
from .models import User
from apps.appointments.models import Appointment


class UserRegistrationView(CreateView):
    """View for user registration."""

    model = User
    form_class = UserRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Registration successful! Please log in.")
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("user_dashboard")
        return super().dispatch(request, *args, **kwargs)


def login_view(request):
    """View for user login."""

    if request.user.is_authenticated:
        if request.user.is_admin_user:
            return redirect("admin_dashboard")
        return redirect("user_dashboard")

    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Session expires after 1 hour (security)
            request.session.set_expiry(3600)

            messages.success(
                request,
                f"Welcome back, {user.get_full_name() or user.username}!"
            )

            if user.is_admin_user:
                return redirect("admin_dashboard")
            return redirect("user_dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, "registration/login.html", {"form": form})


@login_required
def logout_view(request):
    """View for user logout."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")


@login_required
def user_dashboard(request):
    """Dashboard for regular users."""

    if request.user.is_admin_user:
        return redirect("admin_dashboard")

    appointments = Appointment.objects.filter(
        user=request.user
    ).order_by("-created_at")

    context = {
        "appointments": appointments[:5],
        "total_appointments": appointments.count(),
        "pending_appointments": appointments.filter(status="pending").count(),
        "approved_appointments": appointments.filter(status="approved").count(),
        "rejected_appointments": appointments.filter(status="rejected").count(),
    }

    return render(request, "dashboard/user_dashboard.html", context)


@login_required
def admin_dashboard(request):
    """Dashboard for admin users."""

    if not request.user.is_admin_user:
        messages.error(
            request,
            "You do not have permission to access the admin dashboard."
        )
        return redirect("user_dashboard")

    from apps.services.models import Service

    appointments = Appointment.objects.all().order_by("-created_at")

    context = {
        "appointments": appointments[:10],
        "total_appointments": appointments.count(),
        "pending_appointments": appointments.filter(status="pending").count(),
        "approved_appointments": appointments.filter(status="approved").count(),
        "rejected_appointments": appointments.filter(status="rejected").count(),
        "total_users": User.objects.filter(role="user").count(),
        "total_services": Service.objects.filter(is_active=True).count(),
    }

    return render(request, "dashboard/admin_dashboard.html", context)


@login_required
def profile_view(request):
    """View user profile."""

    user = request.user

    if request.method == "POST":
        form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=user)

    return render(
        request,
        "user_profile/profile.html",
        {
            "form": form,
            "user_obj": user
        }
    )


@login_required
def profile_view(request):
    """Edit user profile."""

    user = request.user

    if request.method == "POST":
        form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("user_dashboard")
    else:
        form = ProfileUpdateForm(instance=user)

    return render(
        request,
        "user_profile/profile.html",
        {"form": form}
    )


@login_required
def change_password(request):
    """Change user password securely."""

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()

            # Keeps user logged in after password change
            update_session_auth_hash(request, user)

            messages.success(
                request,
                "Your password was updated successfully."
            )
            return redirect("profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        "registration/change_password.html",
        {"form": form}
    )