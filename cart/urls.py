from django.urls import path

from cart.views.add_to_cart import AddToCartView
from cart.views.get_cart import GetCartView
from cart.views.remove_from_cart import RemoveFromCartView
from cart.views.clear_cart import ClearCartView

urlpatterns = [
    path("add_to_cart", AddToCartView.as_view(), name="Add to Cart"),
    path("get_cart", GetCartView.as_view(), name="Get Cart"),
    path("remove_from_cart", RemoveFromCartView.as_view(), name="Remove from Cart"),
    path("clear_cart", ClearCartView.as_view(), name="Clear Cart"),
]
