from django.urls import path
from order.view.get_all_orders import GetAllOrderView
from order.view.place_order import PlaceOrderView

urlpatterns = [
    path('orders/', GetAllOrderView.as_view(), name='Get all orders'),
    path('place_order/', PlaceOrderView.as_view(), name='Place Order'),
]
