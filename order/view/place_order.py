from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from order.services.order_service import OrderService


class PlaceOrderView(APIView):
    def post(self, request):
        try:
            from cart.models.cart import Cart
            cart = Cart.objects.get(user=request.user)
            shipping_address = request.data.get('shipping_address')
            billing_address = request.data.get('billing_address')
            order = OrderService.create_order_from_cart(
                cart_id=cart.id,
                shipping_address=shipping_address,
                billing_address=billing_address
            )
            # Optionally, serialize the order for response
            from order.models.order import Order
            order_data = {
                'id': str(order.id),
                'order_number': order.order_number,
                'total_amount': str(order.total_amount),
                'order_status': order.order_status,
                'payment_status': order.payment_status,
                'order_date': order.order_date,
            }
            return Response(order_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
