import logging
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

logger = logging.getLogger(__name__)


class ReindexObjectView(BrowserView):
    """
    Reindex the current object
    """
    template = ViewPageTemplateFile('templates/protected.pt')

    def authenticated(self):
        return self.request.get('_authenticator', False)

    def __call__(self):
        """
        Execute the actual reindex.
        The ploneintranet.async framework provides a plone.protect
        authenticator automatically.
        For manual testing, render a simple form to provide the
        authenticator.
        Please do not disable CSRF protection.
        """
        if self.authenticated():
            if 'attributes' in self.request:
                attributes = self.request['attributes']
                self.context.reindexObject(idxs=attributes)
            else:
                self.context.reindexObject()
        return self.template()
