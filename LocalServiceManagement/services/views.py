from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg
from .models import Review, Service
from .forms import ServiceForm
from professionals.models import Professional

# Vendor add service
@login_required
def add_service(request):
    """
    Allow vendors to create and add new services.
    
    POST: Creates a new service with files
    GET: Returns form for service creation
    """
    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.vendor = request.user
            service.title = service.name  # Set title based on name
            service.save()
            return redirect('vendor_dashboard')
    else:
        form = ServiceForm()

    return render(request, 'services/add_service.html', {'form': form})


# Vendor see their services
@login_required
def vendor_services(request):
    """Display services created by the current vendor."""
    services = Service.objects.filter(vendor=request.user)
    return render(request, 'vendor_services.html', {'services': services})


def services_list(request):
    """
    Display list of all services with search and pagination.
    Supports query parameter 'q' for searching by service name.
    """
    query = request.GET.get('q', '')
    
    if query:
        services = Service.objects.filter(name__icontains=query)
    else:
        services = Service.objects.all()
    
    paginator = Paginator(services, 12)  # 12 per page
    page = request.GET.get('page')
    services = paginator.get_page(page)
    
    return render(request, 'services/services.html', {
        'services': services,
        'query': query
    })

def service_detail(request, service_id):

    service = get_object_or_404(Service, id=service_id)

    professionals = Professional.objects.filter(service=service)

    reviews = Review.objects.filter(service=service)

    return render(request,"services/service_detail.html",{
        "service":service,
        "professionals":professionals,
        "reviews":reviews
    })
def calculate_service_rating(service):
    """Aggregate reviews and update service rating"""
    if service.review_set.exists():
        avg = service.review_set.aggregate(Avg('rating'))['rating__avg']
        service.rating = avg
        service.rating_count = service.review_set.count()
        service.save()