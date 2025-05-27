from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_api.auth_exceptions.user_exceptions import NotValidUserID
from auth_api.services.auth_services.auth_services import AuthServices
from auth_api.services.handlers.exception_handlers import ExceptionHandler
from auth_api.services.helpers import validate_user_uid


class UserDetailView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        try:
            user_id = request.data.get("user_id")
            if validate_user_uid(uid=user_id).is_validated:
                user_details = AuthServices().get_user_details(uid=user_id)
                return Response(
                    data={
                        "message": "User details fetched successfully.",
                        "data": user_details.model_dump(),
                    },
                    status=status.HTTP_200_OK,
                    content_type="application/json",
                )
            else:
                raise NotValidUserID()
        except Exception as e:
            return ExceptionHandler().handle_exception(e)
