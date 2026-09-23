from django.contrib import admin

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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description'
    )

    search_fields = (
        'name',
        'description'
    )

    ordering = (
        'name',
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'category',
        'price',
        'stock',
        'is_available'
    )

    list_filter = (
        'category',
        'is_available'
    )

    search_fields = (
        'name',
        'description',
        'category__name'
    )

    list_editable = (
        'price',
        'stock',
        'is_available'
    )

    list_per_page = 20

    ordering = (
        'name',
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'created_at'
    )

    search_fields = (
        'user__username',
    )

    ordering = (
        '-created_at',
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'cart',
        'product',
        'quantity'
    )

    search_fields = (
        'cart__user__username',
        'product__name'
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'full_name',
        'phone',
        'city',
        'state',
        'pincode',
        'total_amount',
        'status',
        'payment_method',
        'payment_status',
        'created_at'
    )

    list_filter = (
        'status',
        'payment_method',
        'payment_status',
        'state',
        'city',
        'created_at'
    )

    search_fields = (
        'user__username',
        'full_name',
        'phone',
        'address',
        'city',
        'state',
        'pincode'
    )

    ordering = (
        '-created_at',
    )

    list_per_page = 20


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'product',
        'quantity',
        'price'
    )

    search_fields = (
        'product__name',
        'order__user__username'
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'product',
        'created_at'
    )

    search_fields = (
        'user__username',
        'product__name'
    )

    ordering = (
        '-created_at',
    )


@admin.register(SavedAddress)
class SavedAddressAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'full_name',
        'phone',
        'city',
        'state',
        'pincode',
        'created_at'
    )

    list_filter = (
        'state',
        'city',
        'created_at'
    )

    search_fields = (
        'user__username',
        'full_name',
        'phone',
        'address',
        'city',
        'state',
        'pincode'
    )

    ordering = (
        '-created_at',
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'product',
        'rating',
        'comment',
        'created_at'
    )

    list_filter = (
        'rating',
        'created_at'
    )

    search_fields = (
        'user__username',
        'product__name',
        'comment'
    )

    ordering = (
        '-created_at',
    )