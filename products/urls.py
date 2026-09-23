from django.urls import path
from . import views


urlpatterns = [

    # ==========================================
    # PRODUCT
    # ==========================================

    path(
        '',
        views.product_list,
        name='product_list'
    ),

    path(
        '<int:id>/',
        views.product_detail,
        name='product_detail'
    ),


    # ==========================================
    # CART
    # ==========================================

    path(
        'cart/',
        views.cart,
        name='cart'
    ),

    path(
        '<int:id>/add-to-cart/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path(
        '<int:id>/buy-now/',
        views.buy_now,
        name='buy_now'
    ),

    path(
        'increase-cart/<int:id>/',
        views.increase_cart_quantity,
        name='increase_cart_quantity'
    ),

    path(
        'decrease-cart/<int:id>/',
        views.decrease_cart_quantity,
        name='decrease_cart_quantity'
    ),

    path(
        'remove-from-cart/<int:id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),


    # ==========================================
    # CHECKOUT
    # ==========================================

    path(
        'checkout/',
        views.checkout,
        name='checkout'
    ),

    path(
        'place-order/',
        views.place_order,
        name='place_order'
    ),

    path(
        'order-success/<int:order_id>/',
        views.order_success,
        name='order_success'
    ),


    # ==========================================
    # ORDERS
    # ==========================================

    path(
        'my-orders/',
        views.my_orders,
        name='my_orders'
    ),

    path(
        'order-detail/<int:order_id>/',
        views.order_detail,
        name='order_detail'
    ),

    path(
        'cancel-order/<int:order_id>/',
        views.cancel_order,
        name='cancel_order'
    ),


    # ==========================================
    # WISHLIST
    # ==========================================

    path(
        'wishlist/',
        views.wishlist,
        name='wishlist'
    ),

    path(
        'add-to-wishlist/<int:id>/',
        views.add_to_wishlist,
        name='add_to_wishlist'
    ),

    path(
        'remove-from-wishlist/<int:id>/',
        views.remove_from_wishlist,
        name='remove_from_wishlist'
    ),


    # ==========================================
    # SAVED DELIVERY ADDRESS
    # ==========================================

    path(
        'saved-addresses/',
        views.saved_addresses,
        name='saved_addresses'
    ),

    path(
        'save-address/',
        views.save_address,
        name='save_address'
    ),

    path(
        'delete-saved-address/<int:id>/',
        views.delete_saved_address,
        name='delete_saved_address'
    ),


    # ==========================================
    # PRODUCT REVIEWS
    # ==========================================

    path(
        '<int:id>/add-review/',
        views.add_review,
        name='add_review'
    ),

    path(
        'delete-review/<int:review_id>/',
        views.delete_review,
        name='delete_review'
    ),
]