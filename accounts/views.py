from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

from products.models import (
    Product,
    Order,
    Review,
    Wishlist
)


def home(request):

    return render(
        request,
        'home.html'
    )


def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect(
                'product_list'
            )

        else:

            messages.error(
                request,
                'Invalid username or password'
            )

    return render(
        request,
        'accounts/login.html'
    )


@login_required
def profile(request):

    user = request.user

    if request.method == 'POST':

        user.first_name = request.POST.get(
            'first_name',
            ''
        )

        user.last_name = request.POST.get(
            'last_name',
            ''
        )

        user.email = request.POST.get(
            'email',
            ''
        )

        user.save()

        messages.success(
            request,
            'Profile updated successfully'
        )

        return redirect(
            'profile'
        )

    return render(
        request,
        'accounts/profile.html',
        {
            'user': user
        }
    )


@staff_member_required
def admin_dashboard(request):

    total_users = User.objects.count()

    total_products = Product.objects.count()

    total_orders = Order.objects.count()

    total_reviews = Review.objects.count()

    total_wishlists = Wishlist.objects.count()

    total_revenue = sum(
        order.total_amount
        for order in Order.objects.all()
        if order.status != 'Cancelled'
    )

    pending_orders = Order.objects.filter(
        status='Pending'
    ).count()

    processing_orders = Order.objects.filter(
        status='Processing'
    ).count()

    shipped_orders = Order.objects.filter(
        status='Shipped'
    ).count()

    delivered_orders = Order.objects.filter(
        status='Delivered'
    ).count()

    cancelled_orders = Order.objects.filter(
        status='Cancelled'
    ).count()

    paid_orders = Order.objects.filter(
        payment_status='Paid'
    ).count()

    pending_payments = Order.objects.filter(
        payment_status='Pending'
    ).count()

    context = {

        'total_users': total_users,

        'total_products': total_products,

        'total_orders': total_orders,

        'total_reviews': total_reviews,

        'total_wishlists': total_wishlists,

        'total_revenue': total_revenue,

        'pending_orders': pending_orders,

        'processing_orders': processing_orders,

        'shipped_orders': shipped_orders,

        'delivered_orders': delivered_orders,

        'cancelled_orders': cancelled_orders,

        'paid_orders': paid_orders,

        'pending_payments': pending_payments,
    }

    return render(
        request,
        'accounts/admin_dashboard.html',
        context
    )