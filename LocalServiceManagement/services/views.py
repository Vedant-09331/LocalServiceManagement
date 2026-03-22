from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg
from urllib3 import request
from .models import Favorite, Review, Service, Category
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
            return redirect('vendors:vendor_dashboard')
    else:
        form = ServiceForm()

    return render(request, 'services/add_service.html', {'form': form})


# Vendor see their services
@login_required
def vendor_services(request):
    """Display services created by the current vendor."""
    services = Service.objects.filter(vendor=request.user)
    return render(request, 'services/vendor_services.html', {'services': services})


def services_list(request):
    """
    Display list of all services with search, location filter and pagination.
    """

    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    sort = request.GET.get('sort', '')

    services = Service.objects.all()

    if query:
        services = services.filter(name__icontains=query) | services.filter(description__icontains=query)
    if category_id:
        services = services.filter(category_id=category_id)

    if sort == 'price_asc':
        services = services.order_by('price')
    elif sort == 'price_desc':
        services = services.order_by('-price')
    elif sort == 'rating':
        services = services.order_by('-rating')

    categories = Category.objects.all()

    paginator = Paginator(services, 12)  # 12 per page
    page = request.GET.get('page')
    services = paginator.get_page(page)

    return render(request, 'services/services.html', {
        'services': services,
        'query': query,
        'category_id': category_id,
        'sort': sort,
        'categories': categories
    })

def service_detail(request, service_id):

    service = get_object_or_404(Service, id=service_id)

    professionals = Professional.objects.filter(service=service)
    reviews = Review.objects.filter(service=service)

    # ✅ FAVORITE LOGIC
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=request.user,
            service=service
        ).exists()

    return render(request, "services/service_detail.html", {
        "service": service,
        "professionals": professionals,
        "reviews": reviews,
        "is_favorite": is_favorite   # ✅ pass to template
    })

def calculate_service_rating(service):
    """Aggregate reviews and update service rating"""
    if service.review_set.exists():
        avg = service.review_set.aggregate(Avg('rating'))['rating__avg']
        service.rating = avg
        service.rating_count = service.review_set.count()
        service.save()

@login_required
def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id, vendor=request.user)
    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            return redirect('vendors:vendor_my_services')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/edit_service.html', {'form': form, 'service': service})

@login_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id, vendor=request.user)
    service.delete()
    return redirect('vendors:vendor_my_services')

@login_required
def add_review(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        Review.objects.create(
            service=service,
            user=request.user,
            rating=rating,
            comment=comment
        )

        # Recalculate service average rating
        aggregated = Review.objects.filter(service=service).aggregate(average=Avg('rating'))
        service.rating = round(aggregated['average'] or 0, 1)
        service.rating_count = Review.objects.filter(service=service).count()
        service.save()

        return redirect('services:service_detail', service_id=service.id)

    return render(request, 'services/add_review.html', {'service': service}) 

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == "POST":
        review.rating = request.POST.get('rating')
        review.comment = request.POST.get('comment')
        review.save()
        return redirect('service_detail', service_id=review.service.id)

    return render(request, 'services/edit_review.html', {'review': review})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    service_id = review.service.id
    review.delete()
    return redirect('service_detail', service_id=service_id)

@login_required
def toggle_favorite(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        service=service
    )

    if not created:
        favorite.delete()  # remove if already exists

    return redirect('services:service_detail', service_id=service.id)

@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, "services/favorite_list.html", {
        "favorites": favorites
    })