"""
Views for user authentication and profile management.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm
from .models import User
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm

class UserRegistrationView(CreateView):
    """View for user registration."""
    
    model = User
    form_class = UserRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Please log in.')
        return response
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('user_dashboard')
        return super().dispatch(request, *args, **kwargs)


def login_view(request):
    """View for user login."""
    
    if request.user.is_authenticated:
        if request.user.is_admin_user:
            return redirect('admin_dashboard')
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                
                # Redirect based on user role
            if user.is_admin_user:
                return redirect('admin_dashboard')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'registration/login.html', {'form': form})


@login_required
def logout_view(request):
    """View for user logout."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def user_dashboard(request):
    """Dashboard for regular users."""
    
    if request.user.is_admin_user:
        return redirect('admin_dashboard')
    
    # Get user's appointments
   
    appointments = appointments.objects.filter(user=request.user).order_by('-created_at')
    
    # Get statistics
    total_appointments = appointments.count()
    pending_appointments = appointments.filter(status='pending').count()
    approved_appointments = appointments.filter(status='approved').count()
    rejected_appointments = appointments.filter(status='rejected').count()
    
    context = {
        'appointments': appointments[:5],  # Latest 5 appointments
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'approved_appointments': approved_appointments,
        'rejected_appointments': rejected_appointments,
    }
    
    return render(request, 'dashboard/user_dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Dashboard for admin users."""
    
    if not request.user.is_admin_user:
        messages.error(request, 'You do not have permission to access the admin dashboard.')
        return redirect('user_dashboard')
    
    # Get all appointments
    from apps.appointments.models import Appointment
    appointments = Appointment.objects.all().order_by('-created_at')
    
    # Get statistics
    total_appointments = appointments.count()
    pending_appointments = appointments.filter(status='pending').count()
    approved_appointments = appointments.filter(status='approved').count()
    rejected_appointments = appointments.filter(status='rejected').count()
    
    # Get total users
    total_users = User.objects.filter(role='user').count()
    
    # Get services count
    from apps.services.models import Service
    total_services = Service.objects.filter(is_active=True).count()
    
    context = {
        'appointments': appointments[:10],  # Latest 10 appointments
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'approved_appointments': approved_appointments,
        'rejected_appointments': rejected_appointments,
        'total_users': total_users,
        'total_services': total_services,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def user_profile(request):
    """View for updating user profile with picture upload."""

    if request.method == 'POST':
        # enctype="multipart/form-data" is needed for file uploads
        form = UserProfileForm(
            request.POST,
            request.FILES,   # ← This captures uploaded files!
            instance=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'registration/profile.html', {'form': form})

