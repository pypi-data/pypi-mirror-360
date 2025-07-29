from django.db.models.signals import post_save
from django.dispatch import receiver
from djangoldp.activities.services import (ActivityQueueService,
                                           activity_sending_finished)

from djangoldp_becknld.consts import BAP_URI, BPP_URI, IS_BAP, IS_BPP
from djangoldp_becknld.models.transaction import Transaction


# Both inbox and outbox activities responses can be catched here
@receiver(activity_sending_finished, sender=ActivityQueueService)
def handle_activity_response(sender, response, saved_activity, **kwargs):
    if saved_activity is not None:
        response_body = saved_activity.response_to_json()
    pass


def _get_transaction_uri(server_uri, transaction_id):
    if not server_uri:
        return None
    return server_uri + "/transactions/" + transaction_id + "/"


@receiver(post_save, sender=Transaction)
def handle_transaction_creation(sender, instance, created, **kwargs):
    if created:
        # TODO: What if my server is both BAP & BPP?
        if IS_BAP:
            if not instance.bap_uri:
                # Reverse case only useful for gateways
                instance.bap_uri = instance.urlid
            if not instance.bpp_uri:
                instance.bpp_uri = _get_transaction_uri(
                    BPP_URI, instance.transaction_id
                )

        if IS_BPP:
            if not instance.bpp_uri:
                instance.bpp_uri = instance.urlid
            if not instance.bap_uri:
                instance.bpp_uri = _get_transaction_uri(
                    BAP_URI, instance.transaction_id
                )

        instance.save()


# Send Activity: Sample from djangoldp_notification
# def send_request(target, object_iri, instance, request_type):
#     author = getattr(get_current_user(), 'urlid', 'unknown')
#     # local inbox
#     if target.startswith(settings.SITE_URL):
#         user = Model.resolve_parent(target.replace(settings.SITE_URL, ''))
#         Notification.objects.create(user=user, object=object_iri, type=request_type, author=author)
#     # external inbox
#     else:
#         json = {
#             "@context": settings.LDP_RDF_CONTEXT,
#             "object": object_iri,
#             "author": author,
#             "type": request_type
#         }
#         ActivityQueueService.send_activity(target, json)
