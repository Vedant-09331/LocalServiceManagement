from decimal import Decimal

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from .models import Cart, CartItem
from services.models import Service
from bookings.models import Booking
from payments.models import Payment


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def add_to_cart(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    cart = _get_or_create_cart(request.user)

    item, created = CartItem.objects.get_or_create(cart=cart, service=service)
    if not created:
        item.quantity += 1
        item.save()

    messages.success(request, f'"{service.name}" added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.info(request, 'Item removed from cart.')
    return redirect('cart:cart_detail')


@login_required
def update_quantity(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        action = request.POST.get('action')
        if action == 'increase':
            item.quantity += 1
            item.save()
        elif action == 'decrease' and item.quantity > 1:
            item.quantity -= 1
            item.save()
        elif action == 'decrease' and item.quantity == 1:
            item.delete()
    return redirect('cart:cart_detail')


@login_required
def cart_detail(request):
    cart = _get_or_create_cart(request.user)
    items = cart.items.select_related('service').all()

    context = {
        'cart': cart,
        'items': items,
        'total': cart.total_price,
    }
    return render(request, 'cart/cart_detail.html', context)


@login_required
def checkout(request):
    """Create a Razorpay order for the entire cart and show payment page."""
    import razorpay
    cart = _get_or_create_cart(request.user)
    items = cart.items.select_related('service').all()

    if not items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    total = cart.total_price  # Decimal
    amount_paise = int(total * 100)  # Razorpay expects amount in paise

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    order_data = {
        'amount': amount_paise,
        'currency': 'INR',
        'payment_capture': 1,
    }
    razorpay_order = client.order.create(data=order_data)

    context = {
        'cart': cart,
        'items': items,
        'total': total,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount_paise': amount_paise,
        'user_email': request.user.email,
    }
    return render(request, 'cart/checkout.html', context)


@login_required
def payment_callback(request):
    """Verify Razorpay payment signature, create bookings, clear cart."""
    import razorpay
    if request.method != 'POST':
        return redirect('cart:cart_detail')

    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    razorpay_signature = request.POST.get('razorpay_signature', '')

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
    except razorpay.errors.SignatureVerificationError:
        messages.error(request, 'Payment verification failed.')
        return redirect('cart:cart_detail')

    # Payment verified — create bookings for each cart item
    cart = _get_or_create_cart(request.user)
    items = cart.items.select_related('service').all()
    bookings_created = []

    for item in items:
        booking = Booking.objects.create(
            user=request.user,
            service=item.service,
            vendor=item.service.vendor.vendor if hasattr(item.service.vendor, 'vendor') else None,
            status='confirmed',
            payment_status='paid',
        )
        Payment.objects.create(
            booking=booking,
            amount=item.subtotal,
            payment_method='razorpay',
            payment_status='completed',
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
        )
        bookings_created.append(booking)

    # Clear the cart
    cart.items.all().delete()

    return render(request, 'cart/payment_success.html', {
        'bookings': bookings_created,
        'total': sum(b.service.price for b in bookings_created),
    })
