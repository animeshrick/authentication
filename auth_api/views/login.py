from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_api.export_types.request_data_types.login_user import LoginRequestType
from auth_api.services.auth_services.auth_services import AuthServices
from auth_api.services.handlers.exception_handlers import ExceptionHandler


class LoginView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request: Request):
        try:
            request_data = request.data
            email = request_data.get("email")
            password = request_data.get("password")

            if email and password:
                result = AuthServices.login(
                    request_data=LoginRequestType(**request_data)
                )
                if result:
                    return Response(
                        data={
                            "message": "You are logged in successfully",
                            "data": result,
                        },
                        status=status.HTTP_200_OK,
                        content_type="application/json",
                    )
            else:
                raise ValueError("Email or Password is not in correct format")

        except Exception as e:
            return ExceptionHandler().handle_exception(e)
