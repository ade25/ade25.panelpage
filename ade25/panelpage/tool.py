from five import grok

from zope.interface import Interface
from zope.globalrequest import getRequest

from collective.beaker.interfaces import ISession

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

    def update(self, uuid, answers):
        survey = self.get()
        item_id = uuid
        if item_id in survey:
            survey[item_id] = answers
            return survey[item_id]
        return None

    def remove(self, uuid):
        survey = self.get()
        if uuid in survey:
            del survey[uuid]
            return uuid
