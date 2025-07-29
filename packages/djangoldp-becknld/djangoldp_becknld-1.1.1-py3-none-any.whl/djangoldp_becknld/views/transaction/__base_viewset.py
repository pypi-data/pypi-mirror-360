import json

from django.db import IntegrityError
from djangoldp.activities import ActivityQueueService, as_activitystream
from djangoldp.activities.errors import (ActivityStreamDecodeError,
                                         ActivityStreamValidationError)
from djangoldp.views.ldp_api import LDPAPIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


# see Model.get_subclass_with_rdf_type
class BaseViewset(LDPAPIView):
    permission_classes = [
        AllowAny,
    ]

    def post(self, request, *args, **kwargs):
        try:
            activity = json.loads(request.body, object_hook=as_activitystream)
            activity.validate()
        except ActivityStreamDecodeError:
            return Response(
                "Activity type unsupported", status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        except ActivityStreamValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        try:
            self._handle_activity(activity, **kwargs)
        except IntegrityError:
            return Response(
                {"Unable to save due to an IntegrityError in the receiver model"},
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        # always save activities
        obj = ActivityQueueService._save_sent_activity(
            activity.to_json(),
            local_id=request.path_info,
            success=True,
            type=activity.type,
        )

        response = Response({}, status=status.HTTP_201_CREATED)
        response["Location"] = obj.urlid

        return response

    def _handle_activity(self, activity, **kwargs):
        pass
