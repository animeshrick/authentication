from uuid import UUID

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_api.services.handlers.exception_handlers import ExceptionHandler
from product.services.product_service import ProductService


class GetProductView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        try:
            if not request.data.get("product_id"):
                raise ValueError("product_id is required.")
            try:
                product_uuid = UUID(request.data.get("product_id"))
            except Exception:
                raise ValueError("Invalid product_id format. Must be a valid UUID.")
            subject = ProductService().get_subject_service(product_id=str(product_uuid))
            return Response(
                data={
                    "message": "Product details fetched Successfully.",
                    "data": subject.model_dump(),
                },
                status=status.HTTP_200_OK,
                content_type="application/json",
            )
        except Exception as e:
            return ExceptionHandler().handle_exception(e)
