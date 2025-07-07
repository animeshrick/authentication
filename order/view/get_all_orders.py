from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from order.services.order_service import OrderService

class OrderView(APIView):
    def get(self, request):
        order_id = request.query_params.get('id')
        try:
            if order_id:
                order = OrderService().get_order_by_id(order_id)
                if not order:
                    return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
                return Response(order)
            
            orders = OrderService().get_all_orders()
            return Response(orders)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            order = OrderService().create_order_from_cart(request.user)
            return Response(order, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
