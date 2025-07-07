from django.urls import path

from product.view.get_all_products import AllProductView
from product.view.get_product import GetProductView

urlpatterns = [
    path("all_order", AllProductView.as_view(), name="All-order"),
    path("place_order", GetProductView.as_view(), name="Place-Order"),
]
