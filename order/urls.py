from django.urls import path
from order.view.get_order_by_id import GetOrderByIdView
from order.view.place_order import PlaceOrderView

urlpatterns = [
    path('get_order/', GetOrderByIdView.as_view(), name='Get single order by id'),
    path('place_order/', PlaceOrderView.as_view(), name='Place Order'),
]
