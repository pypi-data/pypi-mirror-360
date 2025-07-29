from django.urls import path

from djangoldp_becknld.views import InboxViewset, OutboxViewset

urlpatterns = (
    path(
        "transactions/<transaction_id>/inbox/",
        InboxViewset.as_view(),
    ),
    path(
        "transactions/<transaction_id>/outbox/",
        OutboxViewset.as_view(),
    ),
)
