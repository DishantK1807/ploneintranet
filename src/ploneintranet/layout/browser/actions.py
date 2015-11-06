# coding=utf-8
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.actions import DeleteConfirmationForm
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from zope.component import getMultiAdapter


class PIDeleteConfirmationForm(DeleteConfirmationForm):
    ''' We need to override this
    because of some problems with the original delete_confirmation form
    See: https://github.com/plone/plone.app.content/issues/38

    Caveat: we need to reimplement all the actions while overriding,
    because of the button.buttonAndHandler implementation
    '''
    template = ViewPageTemplateFile('templates/delete_confirmation.pt')

    def view_url(self):
        ''' Facade to the homonymous plone_context_state method
        '''
        context_state = getMultiAdapter(
            (self.context, self.request),
            name='plone_context_state'
        )
        return context_state.view_url()

    def updateActions(self):
        ''' This method updates the actions to enable some dynamic behaviours

        In particular it understands the request parametes:
         - pat-modal
         - pat-inject

        If pat-modal is truish we add to the action buttons the class
        'close-panel'
        If pat-inject is truish the pat-inject class is added to the form
        and a data attribute data-pat-inject is filled we the value
        read from the request
        '''
        super(PIDeleteConfirmationForm, self).updateActions()

        if self.request.get('pat-modal'):
            self.actions['Delete'].klass = 'close-panel icon-ok-circle'
            self.actions['Cancel'].klass = 'close-panel icon-cancel-circle'
        else:
            self.actions['Delete'].klass = 'icon-ok-circle'
            self.actions['Cancel'].klass = 'icon-cancel-circle'

    @button.buttonAndHandler(_(u'I am sure, delete now'), name='Delete')
    def handle_delete(self, action):
        title = safe_unicode(self.context.Title())
        parent = aq_parent(aq_inner(self.context))

        # has the context object been acquired from a place it should not have
        # been?
        if self.context.aq_chain == self.context.aq_inner.aq_chain:
            parent.manage_delObjects(self.context.getId(), self.request)
            IStatusMessage(self.request).add(
                PMF(u'${title} has been deleted.', mapping={u'title': title}))
        else:
            IStatusMessage(self.request).add(
                PMF(u'"${title}" has already been deleted',
                    mapping={u'title': title})
            )
        self.request.response.setHeader('Content-Type', 'application/json')
        self.request.response.redirect(parent.absolute_url())

    @button.buttonAndHandler(
        _(u'label_cancel', default=u'Cancel'), name='Cancel')
    def handle_cancel(self, action):
        return self.request.response.redirect(self.view_url())
