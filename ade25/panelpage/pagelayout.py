from AccessControl import Unauthorized
from Acquisition import aq_inner
from five import grok
from zope import schema

from zope.component import getMultiAdapter
from zope.lifecycleevent import modified
from zope.interface import alsoProvides
from plone.directives import form

from plone.autoform.interfaces import IFormFieldProvider
from Products.statusmessages.interfaces import IStatusMessage

from ade25.panelpage.panelpage import IPanelPage

from ade25.panelpage import MessageFactory as _


class IPanelPageLayout(form.Schema):
    """ Behavior storing panelpage block order """

    #form.mode(panelPageLayout='hidden')
    panelPageLayout = schema.List(
        title=_("Panel Page Layout"),
        value_type=schema.TextLine(
            title=_(u"Content Page Layout"),
        ),
        required=False,
    )

alsoProvides(IPanelPageLayout, IFormFieldProvider)


class LayoutChanger(grok.View):
    grok.context(IPanelPage)
    grok.require('cmf.ManagePortal')
    grok.name('page-layout')

    def update(self):
        context = aq_inner(self.context)
        if 'form.button.Submit' in self.request:
            authenticator = getMultiAdapter((context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            form = self.request.form
            self.applyLayout(form)

    def applyLayout(self, data):
        context = aq_inner(self.context)
        updated = data['layout']
        setattr(context, 'panelPageLayout', updated)
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The content block has successfully been updated"),
            type='info')
        url = '{0}/@@panelpage-editor'.format(context.absolute_url())
        return self.request.response.redirect(url)
