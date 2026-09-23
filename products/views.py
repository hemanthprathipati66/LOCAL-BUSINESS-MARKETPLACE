from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Avg

from .models import (
    Category,
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Wishlist,
    SavedAddress,
    Review
)


# ==================================================
# PRODUCT LIST + SEARCH + CATEGORY FILTER + PAGINATION
# ==================================================

def product_list(request):

    search = request.GET.get(
        'search',
        ''
    ).strip()

    category_id = request.GET.get(
        'category',
        ''
    ).strip()

    products = Product.objects.filter(
        is_available=True
    )

    categories = Category.objects.all().order_by(
        'name'
    )

    # Search by product name OR category name
    if search:

        products = products.filter(
            name__icontains=search
        ) | products.filter(
            category__name__icontains=search
        )

    # Filter by category
    if category_id:

        products = products.filter(
            category_id=category_id
        )

    # Remove duplicate products
    products = products.distinct()

    # =========================
    # PAGINATION
    # =========================

    paginator = Paginator(
        products,
        6
    )

    page_number = request.GET.get(
        'page'
    )

    page_obj = paginator.get_page(
        page_number
    )

    return render(
        request,
        'products/product_list.html',
        {
            'products': page_obj,
            'page_obj': page_obj,
            'search': search,
            'categories': categories,
            'selected_category': category_id
        }
    )


# ==================================================
# PRODUCT DETAIL
# ==================================================

def product_detail(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    reviews = Review.objects.filter(
        product=product
    ).select_related(
        'user'
    ).order_by(
        '-created_at'
    )

    average_rating = reviews.aggregate(
        Avg('rating')
    )['rating__avg']

    total_reviews = reviews.count()

    return render(
        request,
        'products/product_detail.html',
        {
            'product': product,
            'reviews': reviews,
            'average_rating': average_rating,
            'total_reviews': total_reviews
        }
    )


# ==================================================
# ADD REVIEW
# ==================================================

@login_required
def add_review(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    if request.method != 'POST':

        messages.error(
            request,
            'Invalid review request.'
        )

        return redirect(
            'product_detail',
            id=product.id
        )

    rating = request.POST.get(
        'rating'
    )

    comment = request.POST.get(
        'comment',
        ''
    ).strip()

    # Check rating
    try:

        rating = int(rating)

    except (
        TypeError,
        ValueError
    ):

        messages.error(
            request,
            'Please select a valid rating.'
        )

        return redirect(
            'product_detail',
            id=product.id
        )

    # Rating must be between 1 and 5
    if rating < 1 or rating > 5:

        messages.error(
            request,
            'Rating must be between 1 and 5 stars.'
        )

        return redirect(
            'product_detail',
            id=product.id
        )

    # Comment is required
    if not comment:

        messages.error(
            request,
            'Please enter a comment.'
        )

        return redirect(
            'product_detail',
            id=product.id
        )

    Review.objects.create(
        user=request.user,
        product=product,
        rating=rating,
        comment=comment
    )

    messages.success(
        request,
        'Review added successfully!'
    )

    return redirect(
        'product_detail',
        id=product.id
    )


# ==================================================
# DELETE OWN REVIEW
# ==================================================

@login_required
def delete_review(request, review_id):

    review = get_object_or_404(
        Review,
        id=review_id,
        user=request.user
    )

    product_id = review.product.id

    if request.method == 'POST':

        review.delete()

        messages.success(
            request,
            'Review deleted successfully.'
        )

    return redirect(
        'product_detail',
        id=product_id
    )


# ==================================================
# CART
# ==================================================

@login_required
def add_to_cart(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    # Check product availability
    if not product.is_available:

        messages.error(
            request,
            'This product is currently unavailable.'
        )

        return redirect(
            'product_detail',
            id=product.id
        )

    # Check stock
    if product.stock <= 0:

        messages.error(
            request,
            'Sorry, this product is out of stock.'
        )

        return redirect(
            'product_detail',
            id=product.id
        )

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if created:

        messages.success(
            request,
            f'{product.name} added to cart successfully!'
        )

    else:

        if cart_item.quantity < product.stock:

            cart_item.quantity += 1
            cart_item.save()

            messages.success(
                request,
                f'{product.name} quantity increased in cart.'
            )

        else:

            messages.warning(
                request,
                'You have reached the available stock limit.'
            )

    return redirect('cart')


# ==================================================
# BUY NOW
# ==================================================

@login_required
def buy_now(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    # Check product availability
    if not product.is_available:

        messages.error(
            request,
            'This product is currently unavailable.'
        )

        return redirect(
            'product_detail',
            id=product.id
        )

    if product.stock <= 0:

        messages.error(
            request,
            'Sorry, this product is out of stock.'
        )

        return redirect(
            'product_detail',
            id=product.id
        )

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:

        if cart_item.quantity < product.stock:

            cart_item.quantity += 1
            cart_item.save()

        else:

            messages.warning(
                request,
                'You have reached the available stock limit.'
            )

            return redirect('checkout')

    messages.success(
        request,
        f'Proceeding to checkout for {product.name}.'
    )

    return redirect('checkout')


# ==================================================
# CART PAGE
# ==================================================

@login_required
def cart(request):

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_items = CartItem.objects.filter(
        cart=cart
    )

    total = 0

    for item in cart_items:

        total += (
            item.product.price *
            item.quantity
        )

    return render(
        request,
        'products/cart.html',
        {
            'cart': cart,
            'cart_items': cart_items,
            'total': total
        }
    )


# ==================================================
# INCREASE CART QUANTITY
# ==================================================

@login_required
def increase_cart_quantity(request, id):

    cart_item = get_object_or_404(
        CartItem,
        id=id,
        cart__user=request.user
    )

    if cart_item.quantity < cart_item.product.stock:

        cart_item.quantity += 1
        cart_item.save()

        messages.success(
            request,
            'Cart quantity increased.'
        )

    else:

        messages.warning(
            request,
            'You have reached the available stock limit.'
        )

    return redirect('cart')


# ==================================================
# DECREASE CART QUANTITY
# ==================================================

@login_required
def decrease_cart_quantity(request, id):

    cart_item = get_object_or_404(
        CartItem,
        id=id,
        cart__user=request.user
    )

    if cart_item.quantity > 1:

        cart_item.quantity -= 1
        cart_item.save()

        messages.success(
            request,
            'Cart quantity decreased.'
        )

    else:

        cart_item.delete()

        messages.success(
            request,
            'Product removed from cart.'
        )

    return redirect('cart')


# ==================================================
# REMOVE FROM CART
# ==================================================

@login_required
def remove_from_cart(request, id):

    cart_item = get_object_or_404(
        CartItem,
        id=id,
        cart__user=request.user
    )

    cart_item.delete()

    messages.success(
        request,
        'Product removed from cart.'
    )

    return redirect('cart')


# ==================================================
# CHECKOUT
# ==================================================

@login_required
def checkout(request):

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_items = CartItem.objects.filter(
        cart=cart
    )

    total = 0

    for item in cart_items:

        total += (
            item.product.price *
            item.quantity
        )

    saved_addresses = SavedAddress.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'products/checkout.html',
        {
            'cart': cart,
            'cart_items': cart_items,
            'total': total,
            'saved_addresses': saved_addresses
        }
    )


# ==================================================
# PLACE ORDER
# ==================================================

@login_required
def place_order(request):

    if request.method != 'POST':

        messages.error(
            request,
            'Invalid order request.'
        )

        return redirect('checkout')

    full_name = request.POST.get(
        'full_name'
    )

    phone = request.POST.get(
        'phone'
    )

    address = request.POST.get(
        'address'
    )

    city = request.POST.get(
        'city'
    )

    state = request.POST.get(
        'state'
    )

    pincode = request.POST.get(
        'pincode'
    )

    if not all([
        full_name,
        phone,
        address,
        city,
        state,
        pincode
    ]):

        messages.error(
            request,
            'Please fill in all delivery address fields.'
        )

        return redirect('checkout')

    payment_method = request.POST.get(
        'payment_method'
    )

    if payment_method not in [
        'COD',
        'UPI',
        'CARD'
    ]:

        messages.error(
            request,
            'Please select a valid payment method.'
        )

        return redirect('checkout')

    if payment_method == 'COD':

        payment_status = 'Pending'

    else:

        payment_status = 'Paid'

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    cart_items = CartItem.objects.filter(
        cart=cart
    )

    if not cart_items.exists():

        messages.error(
            request,
            'Your cart is empty.'
        )

        return redirect('cart')

    with transaction.atomic():

        total = 0

        for item in cart_items:

            if item.quantity > item.product.stock:

                messages.error(
                    request,
                    f'Not enough stock available for {item.product.name}.'
                )

                return redirect('cart')

            total += (
                item.product.price *
                item.quantity
            )

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            status='Pending',
            payment_method=payment_method,
            payment_status=payment_status,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            state=state,
            pincode=pincode
        )

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            item.product.stock -= item.quantity

            item.product.save()

        cart_items.delete()

    messages.success(
        request,
        'Your order has been placed successfully!'
    )

    return redirect(
        'order_success',
        order_id=order.id
    )


# ==================================================
# ORDER SUCCESS
# ==================================================

@login_required
def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        'products/order_success.html',
        {
            'order': order
        }
    )


# ==================================================
# MY ORDERS
# ==================================================

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'products/my_orders.html',
        {
            'orders': orders
        }
    )


# ==================================================
# ORDER DETAIL
# ==================================================

@login_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    order_items = OrderItem.objects.filter(
        order=order
    )

    return render(
        request,
        'products/order_detail.html',
        {
            'order': order,
            'order_items': order_items
        }
    )


# ==================================================
# CANCEL ORDER
# ==================================================

@login_required
def cancel_order(request, order_id):

    if request.method != 'POST':

        messages.error(
            request,
            'Invalid cancellation request.'
        )

        return redirect(
            'order_detail',
            order_id=order_id
        )

    with transaction.atomic():

        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )

        if order.status not in [
            'Pending',
            'Processing'
        ]:

            messages.error(
                request,
                'This order cannot be cancelled now.'
            )

            return redirect(
                'order_detail',
                order_id=order.id
            )

        order_items = OrderItem.objects.filter(
            order=order
        )

        for item in order_items:

            product = item.product

            product.stock += item.quantity

            product.save()

        order.status = 'Cancelled'

        order.save()

    messages.success(
        request,
        f'Order #{order.id} cancelled successfully.'
    )

    return redirect(
        'order_detail',
        order_id=order.id
    )


# ==================================================
# WISHLIST
# ==================================================

@login_required
def add_to_wishlist(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:

        messages.success(
            request,
            f'{product.name} added to wishlist!'
        )

    else:

        messages.info(
            request,
            f'{product.name} is already in your wishlist.'
        )

    return redirect('wishlist')


@login_required
def wishlist(request):

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('product')

    return render(
        request,
        'products/wishlist.html',
        {
            'wishlist_items': wishlist_items
        }
    )


@login_required
def remove_from_wishlist(request, id):

    wishlist_item = get_object_or_404(
        Wishlist,
        id=id,
        user=request.user
    )

    wishlist_item.delete()

    messages.success(
        request,
        'Product removed from wishlist.'
    )

    return redirect('wishlist')


# ==================================================
# SAVED DELIVERY ADDRESS
# ==================================================

@login_required
def saved_addresses(request):

    addresses = SavedAddress.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'products/saved_addresses.html',
        {
            'addresses': addresses
        }
    )


@login_required
def save_address(request):

    if request.method != 'POST':

        messages.error(
            request,
            'Invalid address request.'
        )

        return redirect('checkout')

    full_name = request.POST.get(
        'full_name'
    )

    phone = request.POST.get(
        'phone'
    )

    address = request.POST.get(
        'address'
    )

    city = request.POST.get(
        'city'
    )

    state = request.POST.get(
        'state'
    )

    pincode = request.POST.get(
        'pincode'
    )

    if not all([
        full_name,
        phone,
        address,
        city,
        state,
        pincode
    ]):

        messages.error(
            request,
            'Please fill in all address fields.'
        )

        return redirect('checkout')

    SavedAddress.objects.create(
        user=request.user,
        full_name=full_name,
        phone=phone,
        address=address,
        city=city,
        state=state,
        pincode=pincode
    )

    messages.success(
        request,
        'Address saved successfully!'
    )

    return redirect('saved_addresses')


@login_required
def delete_saved_address(request, id):

    if request.method != 'POST':

        messages.error(
            request,
            'Invalid delete request.'
        )

        return redirect('saved_addresses')

    saved_address = get_object_or_404(
        SavedAddress,
        id=id,
        user=request.user
    )

    saved_address.delete()

    messages.success(
        request,
        'Saved address deleted successfully.'
    )

    return redirect('saved_addresses')