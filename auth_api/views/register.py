from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_api.export_types.request_data_types.register_user import RegisterUserRequestType
from auth_api.services.auth_services.auth_services import AuthServices
from auth_api.services.handlers.exception_handlers import ExceptionHandler


class RegisterUsersView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request: Request):
        try:
            result = AuthServices.create_new_user_service(
                request_data=RegisterUserRequestType(**request.data)
            )
            if result.get("successMessage"):
                return Response(
                    data={
                        "message": result.get("successMessage"),
                        "data": result.get("data"),
                    },
                    status=status.HTTP_201_CREATED,
                    content_type="application/json",
                )
        except Exception as e:
            return ExceptionHandler().handle_exception(e)
