from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_api.services.helpers import validate_user_uid
from cart.export_types.request_data_types.add_to_cart import AddToCartRequestType
from cart.services.cart_services import CartServices
from auth_api.services.handlers.exception_handlers import ExceptionHandler


class AddToCartView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request: Request):
        try:
            user_id = request.data.get("user_id")

            if not user_id:
                raise ValueError("user_id is required")

            if not validate_user_uid(uid=user_id).is_validated:
                raise ValueError("Invalid user_id format")

            result = CartServices.add_items_to_cart(
                request_data=AddToCartRequestType(**request.data)
            )

            if result:
                return Response(
                    data={
                        "message": "Products added to cart successfully.",
                        "data": result.model_dump(),
                    },
                    status=status.HTTP_201_CREATED,
                    content_type="application/json",
                )
            else:
                raise ValueError("Failed to add items to cart")

        except Exception as e:
            return ExceptionHandler().handle_exception(e) 