# Receive Application notification
# Ensure their format
# If 20X: Forward them to the transation's bpp via DjangoLDP Activity Queue
# Respond 200, 201, 403, 404, 40X*
from .__base_viewset import BaseViewset


class OutboxViewset(BaseViewset):
    def _handle_activity(self, activity, **kwargs):
        if activity.type == "confirm":
            self.handle_confirm_activity(activity, **kwargs)
        elif activity.type == "init":
            self.handle_init_activity(activity, **kwargs)
        elif activity.type == "select":
            self.handle_select_activity(activity, **kwargs)

    def handle_confirm_activity(self, activity, **kwargs):
        pass

    def handle_init_activity(self, activity, **kwargs):
        pass

    def handle_select_activity(self, activity, **kwargs):
        pass
