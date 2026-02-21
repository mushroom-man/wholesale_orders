from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.db.models import Sum

from clients.models import Client
from products.models import Product
from orders.models import Order, OrderLine, StandingOrder, StandingOrderLine


def get_next_delivery_date(delivery_day):
    today = timezone.now().date()
    if delivery_day == 'thursday':
        days_until = (3 - today.weekday()) % 7
    else:
        days_until = (4 - today.weekday()) % 7
    
    if days_until == 0:
        days_until = 7
    
    return today + timedelta(days=days_until)


def get_product_availability(product, delivery_date):
    if not product.available:
        return 'unavailable', 0
    
    if not product.forecast_kg or product.forecast_kg <= 0:
        return 'available', None
    
    order_total = OrderLine.objects.filter(
        order__delivery_date=delivery_date,
        order__status__in=['pending', 'confirmed', 'packed'],
        product=product
    ).aggregate(total=Sum('quantity_ordered_kg'))['total'] or Decimal('0')
    
    day_of_week = 'thursday' if delivery_date.weekday() == 3 else 'friday'
    standing_total = StandingOrderLine.objects.filter(
        standing_order__active=True,
        standing_order__client__delivery_day=day_of_week,
        product=product
    ).aggregate(total=Sum('quantity_kg'))['total'] or Decimal('0')
    
    total_ordered = order_total + standing_total
    remaining = product.forecast_kg - total_ordered
    remaining_percent = (remaining / product.forecast_kg) * 100 if product.forecast_kg > 0 else 100
    
    if remaining_percent <= 10:
        return 'limited', remaining
    
    return 'available', remaining


def client_login(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'client'):
            return redirect('portal:dashboard')
        else:
            logout(request)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            client = Client.objects.get(login_email=email)
            if client.user:
                user = authenticate(request, username=client.user.username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('portal:dashboard')
        except Client.DoesNotExist:
            pass
        
        messages.error(request, 'Invalid email or password')
    
    return render(request, 'portal/login.html')


@login_required
def dashboard(request):
    if not hasattr(request.user, 'client'):
        messages.error(request, 'This account is not linked to a client. Please log in with a client account.')
        logout(request)
        return redirect('portal:login')
    
    client = request.user.client
    recent_orders = Order.objects.filter(client=client).order_by('-delivery_date')[:5]
    standing_orders = StandingOrder.objects.filter(client=client, active=True)
    
    context = {
        'client': client,
        'recent_orders': recent_orders,
        'standing_orders': standing_orders,
    }
    return render(request, 'portal/dashboard.html', context)


@login_required
def new_order(request):
    if not hasattr(request.user, 'client'):
        return redirect('portal:login')
    
    client = request.user.client
    products = Product.objects.filter(active=True)
    next_delivery = get_next_delivery_date(client.delivery_day)
    
    product_list = []
    for product in products:
        status, remaining = get_product_availability(product, next_delivery)
        product_list.append({
            'product': product,
            'status': status,
            'remaining': remaining,
        })
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        has_limited_items = False
        
        order = Order.objects.create(
            client=client,
            delivery_date=next_delivery,
            order_type='adhoc',
            status='pending',
            placed_by=client.business_name,
            notes=notes,
        )
        
        total_kg = Decimal('0')
        total_price = Decimal('0')
        
        for item in product_list:
            product = item['product']
            status = item['status']
            
            if status == 'unavailable':
                continue
                
            qty = request.POST.get(f'qty_{product.id}', '0')
            try:
                qty = Decimal(qty)
                if qty > 0:
                    if status == 'limited':
                        has_limited_items = True
                    
                    line_total = qty * product.base_price_per_kg
                    OrderLine.objects.create(
                        order=order,
                        product=product,
                        quantity_ordered_kg=qty,
                        price_per_kg=product.base_price_per_kg,
                        line_total=line_total,
                    )
                    total_kg += qty
                    total_price += line_total
            except:
                pass
        
        order.total_kg = total_kg
        order.total_price = total_price
        order.save()
        
        if has_limited_items:
            messages.warning(request, f'Order placed for {next_delivery}. Note: Some items have limited stock - we will confirm final quantities and adjust pricing if needed.')
        else:
            messages.success(request, f'Order placed for {next_delivery}')
        
        return redirect('portal:order_detail', order_id=order.id)
    
    context = {
        'client': client,
        'product_list': product_list,
        'next_delivery': next_delivery,
        'now': timezone.now(),
    }
    return render(request, 'portal/new_order.html', context)


@login_required
def order_detail(request, order_id):
    if not hasattr(request.user, 'client'):
        return redirect('portal:login')
    
    client = request.user.client
    order = get_object_or_404(Order, id=order_id, client=client)
    
    context = {
        'order': order,
    }
    return render(request, 'portal/order_detail.html', context)


@login_required
def order_history(request):
    if not hasattr(request.user, 'client'):
        return redirect('portal:login')
    
    client = request.user.client
    orders = Order.objects.filter(client=client).order_by('-delivery_date')
    
    context = {
        'orders': orders,
    }
    return render(request, 'portal/order_history.html', context)


@login_required
def standing_orders(request):
    if not hasattr(request.user, 'client'):
        return redirect('portal:login')
    
    client = request.user.client
    standing = StandingOrder.objects.filter(client=client)
    
    context = {
        'standing_orders': standing,
    }
    return render(request, 'portal/standing_orders.html', context)


def client_logout(request):
    logout(request)
    return redirect('portal:login')