"""
URL patterns for accounts app.
"""
from django.urls import path
from . import views

urlpatterns = [
     # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # notification
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_view, name='profile_edit'),
    # Password
    path("change-password/", views.change_password, name="change_password"),
]