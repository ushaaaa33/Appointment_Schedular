from django.shortcuts import render, get_object_or_404
from .models import Service


def service_list(request):
    services = Service.objects.filter(is_active=True).order_by("name")
    return render(request, "services/service_list.html", {
        "services": services
    })


def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk, is_active=True)
    return render(request, "services/service_detail.html", {
        "service": service
    })
