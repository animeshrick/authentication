from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_api.services.auth_services.auth_services import AuthServices
from auth_api.services.handlers.exception_handlers import ExceptionHandler


class ForgotPasswordView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        try:
            email = request.data.get("email")
            new_password = request.data.get("new_password")
            forgot_password_response: str = AuthServices().forgot_password_service(email=email,
                                                                                   new_password=new_password)
            return Response(
                data={
                    "message": forgot_password_response,
                },
                status=status.HTTP_200_OK,
                content_type="application/json",
            )
        except Exception as e:
            return ExceptionHandler().handle_exception(e)
