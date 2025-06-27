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
            if validate_user_uid(uid=user_id).is_validated:
                export_cart = CartServices.add_items_to_cart(request_data=AddToCartRequestType(**request.data))
                return Response(
                    data={
                        "message": "Products added to cart successfully.",
                        "data": export_cart.dict(),
                    },
                    status=status.HTTP_201_CREATED,
                    content_type="application/json"
                )

        except Exception as e:
            return ExceptionHandler().handle_exception(e)
