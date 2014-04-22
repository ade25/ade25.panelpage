import json
from five import grok
from plone import api

from zope.interface import Interface
from zope.globalrequest import getRequest
from zope.lifecycleevent import modified

from plone.app.layout.navigation.interfaces import INavigationRoot
from collective.beaker.interfaces import ISession
from plone.uuid.interfaces import IUUID

from ade25.panelpage.contentblock import IContentBlock

SESSION_KEY = 'Uh53dAfH2JPzI/lIhBvN72RJzZVv6zk5'


class IPageLayoutTool(Interface):
    """ Survey processing tool that stores data inside a beaker session
        storage. The data is then saved as survey participation result
    """

    def get(context):
        """ Get active survey session

            @param uuid: optional catalog uuid of active participation
        """

    def destroy(context):
        """ Destroy a survey session on submitting or by user
            interaction
        """

    def add(context):
        """ Add answers to a survey session or update existing data

            @param uuid: catalog uuid of participation object
            @param answers: serialized form data of survey answers
        """

    def update(context):
        """ Update potentially autosaved form data in session
            storage

            @param uuid: catalog uuid of participation object
            @param answers: serialized survey form data
        """

    def remove(context):
        """ Remove answers from the session

            @param uuid: catalog uuid of participation object
        """


class PageLayoutTool(grok.GlobalUtility):
    grok.provides(IPageLayoutTool)

    def get(self, key=None):
        portal = api.portal.get()
        session_id = 'ppe.session.{0}'.format(SESSION_KEY)
        if key is not None:
            session_id = 'ppe.session.{0}'.format(key)
        session = ISession(getRequest())
        if session_id not in session:
            session[session_id] = dict()
            session.save()
        return session[session_id]

    def destroy(self, key=None):
        session_id = 'ppe.session.{0}'.format(SESSION_KEY)
        if key is not None:
            session_id = 'ppe.session.{0}'.format(key)
        session = ISession(getRequest())
        if session_id in session:
            del session[session_id]
            session.save()

    def add(self, uuid, items=None):
        """
            Add item to survey session
        """
        session = self.get()
        item = self.update(uuid, items)
        if not item:
            session[uuid] = items
            return session[uuid]

    def update(self, uuid, items):
        survey = self.get()
        item_id = uuid
        if item_id in survey:
            survey[item_id] = items
            return survey[item_id]
        return None

    def remove(self, uuid):
        survey = self.get()
        if uuid in survey:
            del survey[uuid]
            return uuid


class UpdateBlockLayoutStorage(grok.View):
    grok.context(INavigationRoot)
    grok.require('cmf.ManagePortal')
    grok.name('migrate-pp-contentblocks')

    def render(self):
        processed = self.process_migration()
        return processed

    def items(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IContentBlock.__identifier__)
        return items

    def process_migration(self):
        idx = 0
        for item in self.items():
            obj = item.getObject()
            #cb_layout = getattr(obj, 'contentBlockLayout')
            #if cb_layout is None:
            #    stored = {}
            #    uid = IUUID(obj)
            #    col_size = 12
            #    col = {
            #        'uuid': uid,
            #        'component': u"placeholder",
            #        'grid-col': col_size
            #    }
            #    stored.append(col)
            setattr(obj, 'contentBlockLayout', '')
            modified(obj)
            obj.reindexObject(idxs='modified')
            idx += 1
        return idx
