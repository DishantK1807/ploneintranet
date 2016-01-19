from Products.Five.browser import BrowserView
from plone import api
from zope.component import adapter, queryMultiAdapter, queryUtility
from ploneintranet.search.solr.interfaces import IConnectionConfig, IConnection

class SolrOptimizeView(BrowserView):
    """
    View to start solr optimization.
    """

    _connection = None

    def __call__(self):
        self._solr.optimize(waitSearcher=None)

    @property
    def _solr_conf(self):
        return queryUtility(IConnectionConfig)

    @property
    def _solr(self):
        if self._connection is None:
            self._connection = IConnection(self._solr_conf)
        return self._connection
