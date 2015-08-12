# coding=utf-8
from DateTime import DateTime
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.memoize.view import memoize
from ploneintranet.core import ploneintranetCoreMessageFactory as _


class ActivityView(BrowserView):
    ''' This view renders an activity
    '''

    as_post = ViewPageTemplateFile('templates/activity_as_post.pt')
    newpostbox_placeholder = _(u'leave_a_comment',
                               default=u'Leave a comment...')

    @property
    @memoize
    def is_anonymous(self):
        ''' Return the portal object
        '''
        return api.user.is_anonymous()

    @property
    @memoize
    def portal(self):
        ''' Return the portal object
        '''
        return api.portal.get()

    @property
    @memoize
    def portal_url(self):
        ''' Return the portal object url
        '''
        return self.portal.absolute_url()

    @property
    @memoize
    def context_url(self):
        ''' Return the context url
        '''
        return self.portal_url

    @property
    @memoize
    def toggle_like(self):
        ''' This is used to render the toggle like stuff
        '''
        toggle_like_base = api.content.get_view(
            'toggle_like_statusupdate',
            self.portal,
            self.request,
        )
        toggle_like_view = toggle_like_base.publishTraverse(
            self.request,
            self.context.getId,
        )
        return toggle_like_view

    @property
    @memoize
    def newpostbox_view(self):
        ''' Return the newpostbox.tile view
        '''
        return api.content.get_view(
            'newpostbox.tile',
            self.portal,
            self.request,
        )

    @property
    @memoize
    def statusupdate_view(self):
        ''' Return the newpostbox.tile view
        '''
        return api.content.get_view(
            'statusupdate_view',
            self.context.context,
            self.request,
        )
