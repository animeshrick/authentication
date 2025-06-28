from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_api.services.helpers import validate_user_uid
from cart.services.cart_services import CartServices
from auth_api.services.handlers.exception_handlers import ExceptionHandler


class RemoveFromCartView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request: Request):
        try:
            user_id = request.data.get("user_id")
            product_id = request.data.get("product_id")

            if not user_id:
                raise ValueError("user_id is required")

            if not product_id:
                raise ValueError("product_id is required")

            if not validate_user_uid(uid=user_id).is_validated:
                raise ValueError("Invalid user_id format")

            result = CartServices.remove_item_from_cart(
                user_id=user_id, product_id=product_id
            )

            return Response(
                data={
                    "message": "Item removed from cart successfully.",
                    "data": result.model_dump(),
                },
                status=status.HTTP_200_OK,
                content_type="application/json",
            )

        except Exception as e:
            return ExceptionHandler().handle_exception(e) 