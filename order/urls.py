from django.urls import path
from order.view.get_all_orders import OrderView

urlpatterns = [
    path('orders/', OrderView.as_view(), name='orders'),  # Handles both GET (list/detail) and POST (create)
]
