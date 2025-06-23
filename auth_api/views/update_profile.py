from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from pydantic import ValidationError

from auth_api.export_types.request_data_types.update_user_profile import (
    UpdateUserProfileRequestType,
)
from auth_api.services.auth_services.auth_services import AuthServices
from auth_api.services.handlers.exception_handlers import ExceptionHandler
from auth_api.services.helpers import validate_user_uid


class UpdateProfileView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            if not user_id:
                return Response(
                    data={"error": "user_id is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                    content_type="application/json",
                )
            validation_result = validate_user_uid(uid=user_id)
            if validation_result.is_validated:
                try:
                    user = AuthServices().update_user_profile(
                        uid=user_id,
                        request_data=UpdateUserProfileRequestType(**request.data),
                    )
                except ValidationError as ve:
                    return Response(
                        data={"error": ve.errors()},
                        status=status.HTTP_400_BAD_REQUEST,
                        content_type="application/json",
                    )
                return Response(
                    data={
                        "message": "User details updated Successfully.",
                        "data": user.model_dump(),
                    },
                    status=status.HTTP_200_OK,
                    content_type="application/json",
                )
            else:
                return Response(
                    data={"error": validation_result.error},
                    status=status.HTTP_400_BAD_REQUEST,
                    content_type="application/json",
                )
        except Exception as e:
            return ExceptionHandler().handle_exception(e)
