# Receive BAP or BPP notifications
# Ensure their format
# Check DjangoLDP ActivityQueue receiver current implementation, may require adaptations
# Consume methods from .inbox: confirm, init, on_confirm, on_init, on_select, select
# confirm, init, select: Send an on_confirm, on_init, on_select to transation's BAP inbox
# Respond 200, 201, 403, 404, 40X
import json

from django.http import Http404
from djangoldp.activities.services import ActivityQueueService
from djangoldp.models import Activity
from rest_framework import status
from rest_framework.response import Response

from djangoldp_becknld.consts import BAP_URI, BECKNLD_CONTEXT, BPP_URI
from djangoldp_becknld.models.item import Item
from djangoldp_becknld.models.transaction import Transaction
from djangoldp_becknld.views.transaction.__base_viewset import (
    BaseViewset, get_transaction_from_activity)


class InboxActivityViewset(BaseViewset):
    def get(self, request, transaction_id, activity_id, *args, **kwargs):
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            if transaction and transaction.urlid:
                activity = Activity.objects.get(id=activity_id)
                serializable_payload = json.loads(activity.payload)
                serializable_payload["@id"] = request.build_absolute_uri()
                serializable_payload["@context"] = BECKNLD_CONTEXT
                # Response is cacheable, as activity should not change
                return Response(
                    serializable_payload,
                    headers={
                        "content-type": "application/ld+json",
                        "Access-Control-Allow-Origin": "*",
                        "Cache-Control": "public, max-age=3600",
                    },
                )
        except Transaction.DoesNotExist or Activity.DoesNotExist:
            pass

        raise Http404


class InboxViewset(BaseViewset):
    def get(self, request, transaction_id, *args, **kwargs):
        response = {
            "@context": BECKNLD_CONTEXT,
            "@id": request.build_absolute_uri(),
            "@type": "ldp:Container",
            "ldp:contains": [],
        }
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            if transaction and transaction.urlid:
                related_activities = Activity.objects.filter(
                    local_id=(transaction.urlid + "inbox/")
                ).order_by("-created_at")

                if related_activities:
                    for activity in related_activities:
                        serializable_payload = json.loads(activity.payload)
                        serializable_payload["@id"] = (
                            activity.local_id + str(activity.id) + "/"
                        )
                        response["ldp:contains"].append(serializable_payload)

                # Response is not cacheable, must revalidate
                response = Response(
                    response,
                    headers={
                        "content-type": "application/ld+json",
                        "Access-Control-Allow-Origin": "*",
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                    },
                )
                return response
        except Transaction.DoesNotExist:
            pass

        raise Http404

    def _handle_activity(self, activity, **kwargs):
        if activity.type == "confirm":
            self.handle_confirm_activity(activity, **kwargs)
        elif activity.type == "init":
            self.handle_init_activity(activity, **kwargs)
        elif activity.type == "select":
            self.handle_select_activity(activity, **kwargs)
        elif activity.type == "on_confirm":
            self.handle_on_confirm_activity(activity, **kwargs)
        elif activity.type == "on_init":
            self.handle_on_init_activity(activity, **kwargs)
        elif activity.type == "on_select":
            self.handle_on_select_activity(activity, **kwargs)

    def handle_confirm_activity(self, activity, **kwargs):
        pass

    def handle_init_activity(self, activity, **kwargs):
        pass

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
                            "@type": ["as:Announce", "beckn:OnSelect"],
                            "type": "on_select",
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
                            "schema:acceptedOffer": {
                                "@type": "schema:Offer",
                                "schema:priceSpecification": {
                                    "@type": "schema:PriceSpecification",
                                    "schema:priceCurrency": "INR",  # TODO: Source?
                                    "schema:price": "0",
                                    "schema:priceComponent": [],
                                },
                            },
                            "schema:potentialAction": {
                                "@type": "schema:ParcelDelivery",  # TODO: How to consider this?
                                # "schema:deliveryAddress": {
                                #     "schema:postalCode": "560001",
                                #     "schema:addressCountry": "IN"
                                # },
                                # "geo:lat": 12.9716,
                                # "geo:long": 77.5946
                            },
                            "beckn:context": {
                                # "beckn:domain": "retail",  # TODO: Where is it defined?
                                # "schema:country": "IND",  # TODO: Country of?
                                # "schema:city": "std:080",  # TODO: City of? (std??)
                                # "beckn:coreVersion": "1.1.0",  # TODO: Where is it defined?
                                "dc:created": str(transaction.update_date),
                            },
                        }

                        # TODO: Don't do that on the fly.
                        # TODO: Generate a real order/offer combination, save them in bpp db

                        total_price = 0
                        for item in ordereditem:
                            item_offered = item["schema:itemOffered"]
                            item_id = item_offered["@id"] if item_offered else None
                            if item_id:
                                quantity = item["schema:orderQuantity"]
                                if quantity:
                                    quantity_value = quantity["schema:value"]
                                    if quantity["schema:unitText"]:
                                        quantity_unit = quantity["schema:unitText"]

                                try:
                                    if quantity_unit:
                                        item_ref = Item.objects.get(
                                            item_id=item_id,
                                            unit_text=quantity_unit,
                                        )
                                    else:
                                        item_ref = Item.objects.get(item_id=item_id)
                                except Item.DoesNotExist:
                                    pass

                                if item_ref:

                                    price = item_ref.unitary_price

                                    if quantity_value:
                                        price *= quantity_value

                                    new_activity["schema:acceptedOffer"][
                                        "schema:priceSpecification"
                                    ]["schema:priceComponent"].append(
                                        {
                                            "@type": "schema:UnitPriceSpecification",
                                            "schema:itemOffered": item_ref.item_id,
                                            "schema:price": str(price),
                                        }
                                    )

                                    total_price += price
                                else:
                                    # TODO: Log this exception
                                    return Response(
                                        "Item not found",
                                        status=status.HTTP_404_NOT_FOUND,
                                    )

                            else:
                                # TODO: Log this exception
                                return Response(
                                    "Item missing @id",
                                    status=status.HTTP_400_BAD_REQUEST,
                                )

                        new_activity["schema:acceptedOffer"][
                            "schema:priceSpecification"
                        ]["price"] = total_price

                        ActivityQueueService.send_activity(
                            transaction.bap_inbox, new_activity
                        )
                        return Response(new_activity, status=status.HTTP_201_CREATED)
                    except Exception:
                        # TODO: Log this exception
                        return Response(
                            "Unable to parse activity",
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                return Response(
                    "Missing schema:orderedItem", status=status.HTTP_400_BAD_REQUEST
                )
            return Response("Missing as:object", status=status.HTTP_400_BAD_REQUEST)

        return Response("Transaction not found", status=status.HTTP_404_NOT_FOUND)

    def handle_on_confirm_activity(self, activity, **kwargs):
        pass

    def handle_on_init_activity(self, activity, **kwargs):
        pass

    def handle_on_select_activity(self, activity, **kwargs):
        print("received on_select activity")
        print(activity)
        pass
