from plone import api
from Products.Five import BrowserView


class WorkspaceGroupView(BrowserView):
    """Helper view to show the members of a group when clicked in workspace"""

    def group(self):
        """ Get group data """
        gid = self.request.get('id')
        if not gid:
            return dict(id='',
                        title="No Group",
                        description="",
                        members=[])

        g = api.group.get(groupname=gid)
        m = api.user.get_users(groupname=gid)

        title = g.title or gid
        description = g.description

        if ':' in gid:
            role, uid = gid.split(':')
            ws = api.content.get(UID=uid)
            title = ws.Title()
            description = ws.Description()

        return dict(id=gid,
                    title=title,
                    description=description,
                    members=m)
