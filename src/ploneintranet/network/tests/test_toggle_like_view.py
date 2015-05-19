# -*- coding: utf-8 -*-
from plone import api
from plone.app.discussion.interfaces import IConversation
from plone.uuid.interfaces import IUUID
from ploneintranet.core.integration import PLONEINTRANET
from ploneintranet.microblog.statusupdate import StatusUpdate
from ploneintranet.network.interfaces import INetworkTool
from ploneintranet.network.testing import IntegrationTestCase
from ploneintranet.network.testing import set_browserlayer
from zope.component import createObject
from zope.component import getUtility


class TestToggleLikeView(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)
        self.util = getUtility(INetworkTool)
        self.doc1 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
            title='Doc 1'
        )
        self.user_id = api.user.get_current().getId()

    def test_show_like(self):
        view = api.content.get_view('toggle_like', self.doc1, self.request)
        item_id = api.content.get_uuid(self.doc1)
        output = view()
        self.assertIn('like_button', output)
        self.assertFalse(
            self.util.is_liked("content", item_id, self.user_id))

    def test_toggle_like(self):
        self.request.form['like_button'] = 'like'
        view = api.content.get_view('toggle_like', self.doc1, self.request)
        item_id = api.content.get_uuid(self.doc1)

        # Toggle like for doc1 on
        output = view()
        self.assertIn('(1)', output)
        self.assertIn('Unlike', output)
        user_likes = self.util.get_likes("content", self.user_id)

        self.assertTrue(
            self.util.is_liked("content", item_id, self.user_id))
        self.assertEqual(len(user_likes), 1)

        # Toggle like for doc1 off
        output = view()
        user_likes = self.util.get_likes("content", self.user_id)
        self.assertEqual(len(user_likes), 0)
        self.assertIn('(0)', output)
        self.assertIn('Like', output)

    def test_like_discussion_item(self):
        # test discussion-item
        conversation = IConversation(self.doc1)
        comment1 = createObject('plone.Comment')
        conversation.addComment(comment1)
        comment = [i for i in conversation.getComments()][0]
        comment_id = IUUID(comment)

        self.request.form['like_button'] = 'like'
        view = api.content.get_view('toggle_like', comment, self.request)

        # Toggle like for comment on
        output = view()
        self.assertIn('(1)', output)
        self.assertIn('Unlike', output)
        user_likes = self.util.get_likes("content", self.user_id)

        self.assertTrue(
            self.util.is_liked("content", comment_id, self.user_id))
        self.assertEqual(len(user_likes), 1)

        # Toggle like for comment off
        output = view()
        user_likes = self.util.get_likes("content", self.user_id)
        self.assertEqual(len(user_likes), 0)
        self.assertIn('(0)', output)
        self.assertIn('Like', output)

    def test_like_status_update(self):
        # test statusupdate
        su = StatusUpdate('Some cool news!')
        container = PLONEINTRANET.microblog
        container.add(su)
        update_id = str(su.id)

        self.request.form['like_button'] = 'like'
        view = api.content.get_view('toggle_like_statusupdate',
                                    self.portal, self.request)
        self.assertRaises(KeyError, view)
        view = view.publishTraverse(self.request, update_id)

        # Toggle like for statusupdate on
        output = view()
        self.assertIn('(1)', output)
        self.assertIn('Unlike', output)
        user_likes = self.util.get_likes("update", self.user_id)

        self.assertTrue(
            self.util.is_liked("update", update_id, self.user_id))
        self.assertEqual(len(user_likes), 1)

        # Toggle like for statusupdate off
        output = view()
        user_likes = self.util.get_likes("update", self.user_id)
        self.assertEqual(len(user_likes), 0)
        self.assertIn('(0)', output)
        self.assertIn('Like', output)
