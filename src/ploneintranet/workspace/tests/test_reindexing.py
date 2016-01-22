# coding=utf-8
from ZPublisher.HTTPRequest import FileUpload
from plone import api
from plone.namedfile.file import NamedBlobFile
from ploneintranet.search.interfaces import ISiteSearch
from ploneintranet.search.solr.interfaces import IConnection
from ploneintranet.search.solr.interfaces import IConnectionConfig
from ploneintranet.workspace.basecontent import utils
from ploneintranet.workspace.interfaces import IWorkspaceAppFormLayer
from ploneintranet.workspace.testing import \
    PLONEINTRANET_WORKSPACE_SOLR_TESTING
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.component import getUtility
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectModifiedEvent

import os
import time
import transaction

TEST_FILENAME = u'test.odt'


class TestReindexing(BaseTestCase):
    """ Test that a comma separated string of tabs is saved as a tuple of
    strings
    """
    layer = PLONEINTRANET_WORKSPACE_SOLR_TESTING

    def setUp(self):
        super(TestReindexing, self).setUp()
        alsoProvides(self.request, IWorkspaceAppFormLayer)
        workspaces = self.portal["workspaces"]
        self.ws = api.content.create(
            workspaces,
            'ploneintranet.workspace.workspacefolder',
            'test-tag-workspace',
            title='Test Tag Workspace',
        )
        self.doc = api.content.create(
            self.ws,
            'Document',
            'tagged-doc',
            'Tagged Document',
        )
        self.startTime = time.time()

        ff = open(os.path.join(os.path.dirname(__file__), TEST_FILENAME), 'r')
        self.filedata = ff.read()
        ff.close()
        self.testfolder = api.content.create(
            type='Folder',
            title=u"Testfolder",
            container=self.portal)
        self.testfile = api.content.create(
            type='File',
            id='test-file',
            title=u"Test File",
            file=NamedBlobFile(data=self.filedata, filename=TEST_FILENAME),
            container=self.testfolder)

        # This is a substitute for transaction.commit(), which causes mayhem
        # somewhere deeper in the test setup.
        # If I call transaction.commit() here, then the workspace container
        # created in BaseTestCase.setUp() reappears after being deleted in
        # BaseTestCase.tearDown(). This goes on to cause an error when
        # the setUp() method tries to re-create the workspace container for the
        # next test
        conn = IConnection(getUtility(IConnectionConfig))
        conn.commit()

    def tearDown(self):
        t = time.time() - self.startTime
        # print running time to compare tests w/ and w/o extra reindexObject()
        print "\nTime of %s: %.3f" % (self.id(), t)
        super(TestReindexing, self).tearDown()
        api.content.delete(obj=self.ws)

    # without unnecessary reindex
    def test_obj_reindex_by_notify(self):
        """Set multiple tags on an object as a comma separated string and
        verify that they are saved as a tuple of strings."""
        self.request.form['title'] = u'New Title'
        utils.dexterity_update(self.doc, self.request)
        self.assertEqual(u'New Title', self.doc.title)
        uid = self.doc.UID()
        notify(ObjectModifiedEvent(self.doc))
        brain = self.portal.portal_catalog.searchResults(UID=uid)[0]
        self.assertEqual(u'New Title', brain.Title)

    # with unnecessary reindex (to compare running times)
    def test_obj_reindex_by_notify_and_reindexobject(self):
        """Set multiple tags on an object as a comma separated string and
        verify that they are saved as a tuple of strings."""
        self.request.form['title'] = u'New Title'
        utils.dexterity_update(self.doc, self.request)
        self.assertEqual(u'New Title', self.doc.title)
        uid = self.doc.UID()
        self.doc.reindexObject()
        notify(ObjectModifiedEvent(self.doc))
        brain = self.portal.portal_catalog.searchResults(UID=uid)[0]
        self.assertEqual(u'New Title', brain.Title)

    def test_obj_reindex_searchable_text(self):
        """Set multiple tags on an object as a comma separated string and
        verify that they are saved as a tuple of strings."""
        self.request.form['title'] = u'Test File New'
        utils.dexterity_update(self.testfile, self.request)
        notify(ObjectModifiedEvent(self.testfile))
        self.assertEqual(u'Test File New', self.testfile.title)
        transaction.commit()

        # solr query for a string contained in test.odt
        sitesearch = getUtility(ISiteSearch)
        response = sitesearch.query(phrase='aaaaa',
                                    step=99999)
        search_result_titles = [res['Title'] for res in response.results]
        self.assertIn(u'Test File New', search_result_titles)

        # upload a new file (test2.odt) for the existing file object
        open_file = open(
            os.path.join(os.path.dirname(__file__), 'test2.odt'), 'r')
        mock_fieldstorage = MockFieldStorage(open_file, 'uploadtestfile', '')
        file_upload = FileUpload(mock_fieldstorage)
        self.request.form['file'] = file_upload
        utils.dexterity_update(self.testfile, self.request)
        notify(ObjectModifiedEvent(self.testfile))
        transaction.commit()

        # solr query for a string contained in test.odt
        sitesearch = getUtility(ISiteSearch)
        response = sitesearch.query(phrase='aaaaa',
                                    step=99999)
        search_result_titles = [res['Title'] for res in response.results]
        self.assertNotIn(u'Test File New', search_result_titles)

        # solr query for a string contained in test2.odt
        sitesearch = getUtility(ISiteSearch)
        response = sitesearch.query(phrase='bbbbb',
                                    step=99999)
        search_result_titles = [res['Title'] for res in response.results]
        self.assertIn(u'Test File New', search_result_titles)


# This class is required to instantiate the FileUpload class
class MockFieldStorage:

    def __init__(self, file, filename, headers):
        self.file = file
        self.filename = filename
        self.headers = headers
