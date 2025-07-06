from django.urls import path

from product.view.get_all_products import AllProductView
from product.view.get_product import GetProductView

urlpatterns = [
    path("all_product", AllProductView.as_view(), name="All-product"),
    path("get_product", GetProductView.as_view(), name="Get-product"),
]
