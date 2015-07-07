# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from plone.memoize.view import memoize
from ploneintranet.notifications.channel import AllChannel
from ploneintranet import api as pi_api


class NotificationsView(BrowserView):

    @memoize
    def your_notifications(self):
        display_message = []
        user = api.user.get_current()
        # TODO a zope user like admin will fail from here
        try:
            channel = AllChannel(user.getUserId())
            display_message = channel.get_all_messages(limit=10)
        except AttributeError:
            # AttributeError: getUserId
            display_message = []
        return display_message

    def get_author_image(self, member_id):
        """
        Fetch the author portrait image url accoding to member_id
        """
        return pi_api.userprofile.avatar_url(member_id)
