"""
Views for displaying and managing services.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Service


class ServiceListView(ListView):
    """View for listing all active services."""
    
    model = Service
    template_name = 'services/services_list.html'
    context_object_name = 'services'
    paginate_by = 9
    
    def get_queryset(self):
        return Service.objects.filter(is_active=True)


class ServiceDetailView(DetailView):
    """View for displaying service details."""
    
    model = Service
    template_name = 'services/services_detail.html'
    context_object_name = 'service'
    
    def get_queryset(self):
        return Service.objects.filter(is_active=True)