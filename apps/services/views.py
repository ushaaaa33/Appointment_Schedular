"""
Views for displaying and managing services with search and filtering.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Service


class ServiceListView(ListView):
    """View for listing all active services with search and filtering."""
    
    model = Service
    template_name = 'services/service_list.html'
    context_object_name = 'services'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True)
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Category filter
        category = self.request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category=category)
        
        # Price range filter
        min_price = self.request.GET.get('min_price', '')
        max_price = self.request.GET.get('max_price', '')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Duration filter
        duration = self.request.GET.get('duration', '')
        if duration == 'short':
            queryset = queryset.filter(duration_minutes__lte=30)
        elif duration == 'medium':
            queryset = queryset.filter(duration_minutes__gt=30, duration_minutes__lte=60)
        elif duration == 'long':
            queryset = queryset.filter(duration_minutes__gt=60)
        
        # Sorting
        sort_by = self.request.GET.get('sort', 'name')
        if sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'duration':
            queryset = queryset.order_by('duration_minutes')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pass filter parameters to template
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['selected_duration'] = self.request.GET.get('duration', '')
        context['selected_sort'] = self.request.GET.get('sort', 'name')
        
        # Get all categories for filter dropdown
        context['categories'] = Service.CATEGORY_CHOICES
        
        # Get price range for filters
        all_services = Service.objects.filter(is_active=True)
        if all_services.exists():
            context['min_service_price'] = all_services.order_by('price').first().price
            context['max_service_price'] = all_services.order_by('-price').first().price
        
        # Get count of results
        context['total_services'] = self.get_queryset().count()
        
        return context


class ServiceDetailView(DetailView):
    """View for displaying service details."""
    
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'
    
    def get_queryset(self):
        return Service.objects.filter(is_active=True)