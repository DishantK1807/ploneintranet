from plone import api
from plone.dexterity.content import Item
from plone.supermodel import model
from ploneintranet.workspace.adapters import IMetroMap
from ploneintranet.workspace.case import ICase
from ploneintranet.workspace.utils import parent_workspace
from zope import schema
from zope.interface import implements

from .. import _
from ..behaviors import ITodoMarker


class ITodo(model.Schema):
    """A todo content type
    """

    title = schema.TextLine(title=_("Task"))


class Todo(Item):
    implements(ITodo, ITodoMarker)

    def reopen(self):
        """
        This only applies to Todo items in Case Workspaces.

        Set the workflow state to "open" if the milestone of the Todo item is
        the same as the current, or earlier workflow state of the Case
        Workspace, otherwise set to "planned".

        Only Open items will appear in the dashboard.
        """
        workspace = parent_workspace(self)
        wft = api.portal.get_tool("portal_workflow")
        if not ICase.providedBy(workspace):
            api.content.transition(self, "set_to_open")
        else:
            milestone = self.milestone
            if not milestone:
                api.content.transition(self, "set_to_planned")
            else:
                workspace_state = wft.getInfoFor(workspace, "review_state")
                mm_seq = IMetroMap(workspace).metromap_sequence.keys()
                if mm_seq.index(milestone) > mm_seq.index(workspace_state):
                    api.content.transition(self, "set_to_planned")
                else:
                    api.content.transition(self, "set_to_open")
