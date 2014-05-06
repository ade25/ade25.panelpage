from five import grok
from plone import api

from zope.interface import Interface
from zope.globalrequest import getRequest
from zope.lifecycleevent import modified

from collective.beaker.interfaces import ISession

SESSION_KEY = 'Uh53dAfH2JPzI/lIhBvN72RJzZVv6zk5'


class IPanelTool(Interface):
    """ Survey processing tool that stores data inside a beaker session
        storage. The data is then saved as survey participation result
    """

    def update(context):
        """ Update panel content

            ::param uuid: catalog uuid of participation object
            ::param component: panel type or component name
            ::param data: serialized edit form data
        """


class PanelTool(grok.GlobalUtility):
    grok.provides(IPanelTool)

    def update(self, uuid, component, data):
        survey = self.get()
        item_id = uuid
        if item_id in survey:
            survey[item_id] = items
            return survey[item_id]
        return None
