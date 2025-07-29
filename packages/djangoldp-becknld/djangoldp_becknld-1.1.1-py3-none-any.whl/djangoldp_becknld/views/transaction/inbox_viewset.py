# Receive BAP or BPP notifications
# Ensure their format
# Check DjangoLDP ActivityQueue receiver current implementation, may require adaptations
# Consume methods from .inbox: confirm, init, on_confirm, on_init, on_select, select
# confirm, init, select: Send an on_confirm, on_init, on_select to transation's BAP inbox
# Respond 200, 201, 403, 404, 40X
from django.conf import settings
from django.http import Http404
from djangoldp.models import Activity
from djangoldp.views.commons import JSONLDRenderer
from rest_framework.response import Response

from djangoldp_becknld.models.transaction import Transaction
from djangoldp_becknld.views.transaction.__base_viewset import BaseViewset


class InboxViewset(BaseViewset):
    renderer_classes = (JSONLDRenderer,)

    def get(self, request, transaction_id, *args, **kwargs):
        response = {
            '@context': settings.LDP_RDF_CONTEXT,
            '@id': request.build_absolute_uri(),
            '@type': 'ldp:Container',
            'ldp:contains': []
        }
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            if transaction and transaction.urlid:
                related_activities = Activity.objects.filter(
                    local_id=(transaction.urlid + "inbox/")
                )

                if related_activities:
                    response['ldp:contains'] = related_activities

                response = Response(response, headers={
                    "content-type": "application/ld+json",
                    'Access-Control-Allow-Origin': '*',
                    'Cache-Control': 'public, max-age=3600',
                })
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
        pass

    def handle_on_confirm_activity(self, activity, **kwargs):
        pass

    def handle_on_init_activity(self, activity, **kwargs):
        pass

    def handle_on_select_activity(self, activity, **kwargs):
        pass
