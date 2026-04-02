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
    # payment
    path("payment/<int:appointment_id>/", views.khalti_payment, name="khalti_payment"),
    path("payment/response/", views.khalti_payment_response, name="khalti_payment_response"),
    # receipt
    path("receipt/<int:appointment_id>/", views.download_receipt, name="download_receipt"),
]