from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_api.services.helpers import validate_user_uid
from cart.services.cart_services import CartServices
from auth_api.services.handlers.exception_handlers import ExceptionHandler
from cart.export_types.request_data_types.get_cart import GetCartRequestType


class GetCartView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request: Request):
        try:
            # Try to get user_id from query params first, then from request body
            user_id = request.query_params.get("user_id")
            
            if not user_id:
                # If not in query params, try to get from request body
                user_id = request.data.get("user_id") if hasattr(request, 'data') else None
            
            if not user_id:
                raise ValueError("user_id is required. Please provide it as a query parameter (?user_id=...) or in the request body.")

            # Validate request data using Pydantic model
            request_data = GetCartRequestType(user_id=user_id)
            
            if not validate_user_uid(uid=str(request_data.user_id)).is_validated:
                raise ValueError("Invalid user_id format")

            result = CartServices.get_user_cart(user_id=str(request_data.user_id))

            return Response(
                data={
                    "message": "Cart details fetched successfully.",
                    "data": result.model_dump(),
                },
                status=status.HTTP_200_OK,
                content_type="application/json",
            )

        except Exception as e:
            return ExceptionHandler().handle_exception(e) 