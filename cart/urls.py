from django.urls import path

from cart.view.add_to_cart import AddToCartView

urlpatterns = [
    path("add_to_cart", AddToCartView.as_view(), name="Add to Cart"),
]
