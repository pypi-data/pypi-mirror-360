# Receive Application notification
# Ensure their format
# If 20X: Forward them to the transation's bpp via DjangoLDP Activity Queue
# Respond 200, 201, 403, 404, 40X*
from djangoldp.activities.services import ActivityQueueService
from rest_framework import status
from rest_framework.response import Response

from djangoldp_becknld.consts import BAP_URI, BECKNLD_CONTEXT, BPP_URI
from djangoldp_becknld.views.transaction.__base_viewset import (
    BaseViewset, get_transaction_from_activity)


class OutboxViewset(BaseViewset):
    def get(self, *args, **kwargs):
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def _handle_activity(self, activity, **kwargs):
        if activity.type == "confirm":
            self.handle_confirm_activity(activity, **kwargs)
        elif activity.type == "init":
            self.handle_init_activity(activity, **kwargs)
        elif activity.type == "select":
            self.handle_select_activity(activity, **kwargs)

    def handle_confirm_activity(self, activity, **kwargs):
        transaction = get_transaction_from_activity(activity)

        if transaction:
            # TODO: forward activity to transaction.bpp_inbox
            return Response({}, status=status.HTTP_201_CREATED)

        return Response({}, status=status.HTTP_404_NOT_FOUND)

    def handle_init_activity(self, activity, **kwargs):
        transaction = get_transaction_from_activity(activity)

        if transaction:
            # TODO: forward activity to transaction.bpp_inbox
            return Response({}, status=status.HTTP_201_CREATED)

        return Response({}, status=status.HTTP_404_NOT_FOUND)

    def handle_select_activity(self, activity, **kwargs):
        transaction = get_transaction_from_activity(activity)

        if transaction:
            object = getattr(activity, "as:object", None)
            if object:
                ordereditem = object["schema:orderedItem"]
                if ordereditem:
                    try:
                        new_activity = {
                            "@context": BECKNLD_CONTEXT,
                            "@type": ["as:Announce", "beckn:Select"],
                            "type": "select",
                            "as:actor": {
                                "@id": transaction.bap_outbox,
                                "schema:name": BAP_URI,  # TODO: Where to find self name?
                            },
                            "as:target": {
                                "@id": transaction.bpp_inbox,
                                "schema:name": BPP_URI,
                            },
                            "as:object": {
                                "@type": "as:Order",  # TODO: Does not exist?
                                "beckn:transactionId": transaction.transaction_id,
                                "schema:orderedItem": ordereditem,
                            },
                            "beckn:context": {
                                # "beckn:domain": "retail",  # TODO: Where is it defined?
                                # "schema:country": "IND",  # TODO: Country of?
                                # "schema:city": "std:080",  # TODO: City of? (std??)
                                # "beckn:coreVersion": "1.1.0",  # TODO: Where is it defined?
                                "dc:created": str(transaction.update_date),
                            },
                        }

                        ActivityQueueService.send_activity(
                            transaction.bpp_inbox, new_activity
                        )

                        return Response(new_activity, status=status.HTTP_201_CREATED)

                    except Exception:
                        # TODO: Log this exception
                        return Response(
                            "Unable to forward activity",
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                return Response(
                    "Missing schema:orderedItem", status=status.HTTP_400_BAD_REQUEST
                )

            return Response("Missing as:object", status=status.HTTP_400_BAD_REQUEST)

        return Response("Transaction not found", status=status.HTTP_404_NOT_FOUND)
