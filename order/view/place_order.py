from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from order.services.order_service import OrderService


class PlaceOrderView(APIView):
    def post(self, request):
        try:
            order = OrderService().create_order_from_cart(request.user)
            return Response(order, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
