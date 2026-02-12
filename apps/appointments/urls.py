"""
URL patterns for appointments app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.AppointmentListView.as_view(), name='appointment_list'),
    path('create/', views.AppointmentCreateView.as_view(), name='appointment_create'),
    path('<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('<int:pk>/update/', views.AppointmentUpdateView.as_view(), name='appointment_update'),
    path('<int:pk>/delete/', views.AppointmentDeleteView.as_view(), name='appointment_delete'),
    path('<int:pk>/approve/', views.appointment_approve, name='appointment_approve'),
    path('<int:pk>/reject/', views.appointment_reject, name='appointment_reject'),
]