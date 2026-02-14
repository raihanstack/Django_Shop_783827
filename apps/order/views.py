from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from .models import Order, Address
from main.models import Config
from apps.cart.views import get_or_create_cart
from .districts import districts

def checkout_view(request):
    """Checkout process"""
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')
    
    # Check stock availability for all items
    for item in cart.items.all():
        if not item.product.can_order(item.quantity):
            messages.error(
                request,
                f'Sorry, {item.product.name} is out of stock or has insufficient quantity.'
            )
            return redirect('cart')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        district = request.POST.get('district')

        if name == '' or email == '' or phone == '' or address == '' or district == '':
            messages.error(request, 'Please fill in all required fields.')
            return redirect('checkout')

        # Create address
        address = Address.objects.create(
            name=name,
            email=email,
            phone=phone,
            district=district,
            address=address,
        )
        # Calculate shipping 
        config = Config.objects.first()
        shipping_cost = config.delivery_cost_dhaka if district == 'Dhaka' else config.delivery_cost
        
        # Create order
        order = Order.create_from_cart(cart, address, shipping_cost)
        
        if order:
            messages.success(request, f'Order {order.order_number} placed successfully!')
            return redirect('confirmation', order_number=order.order_number) 
        else:
            messages.error(request, 'Error placing order. Please try again.')
    
    context = {
        'cart': cart,
        'districts': districts,
        'cart_items': cart.items.select_related('product').all(),
        'subtotal': cart.get_total_price(),
    }
    return render(request, 'order/checkout.html', context)


def confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'order/confirmation.html', {'order': order})

# ============================================================================
# ORDER VIEWS
# ============================================================================

def order_list(request):
    """List user's orders"""
    orders = request.user.get_orders()
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
    }
    return render(request, 'order/history.html', context)


def order_detail(request, order_number):
    """Order detail view"""
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )
    
    order_items = order.items.select_related('product', 'size', 'color').all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'store/order_detail.html', context)

def cancel_order(request, order_number):
    """Cancel an order"""
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )
    
    if order.cancel_order():
        messages.success(request, f'Order {order.order_number} has been cancelled.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    
    return redirect('order_detail', order_number=order.order_number)
