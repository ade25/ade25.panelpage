# -*- coding: utf-8 -*-
"""Module providing genearal toolset for panel management"""

from five import grok
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getUtility
from zope.interface import Interface
from zope.lifecycleevent import modified
from zope.schema import getFieldsInOrder
# from collective.beaker.interfaces import ISession

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
        item = api.content.get(UID=uuid)
        if 'textline' in data:
            setattr(item, 'textline', data['textline'])
        if 'textblock' in data:
            setattr(item, 'textblock', data['textblock'])
        else:
            fti = getUtility(IDexterityFTI,
                             name='ade25.panelpage.panel')
            schema = fti.lookupSchema()
            fields = getFieldsInOrder(schema)
            for key, value in fields:
                try:
                    new_value = data[key]
                    setattr(item, key, new_value)
                except KeyError:
                    continue
        modified(item)
        item.reindexObject(idxs='modified')
        return item
