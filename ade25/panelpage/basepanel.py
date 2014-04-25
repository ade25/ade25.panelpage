from Acquisition import aq_inner
from five import grok
from zope import schema

from plone.dexterity.content import Item

from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable

from ade25.panelpage import MessageFactory as _


class IBasePanel(form.Schema, IImageScaleTraversable):
    """
    A single content panel or box
    """
    title = schema.TextLine(
        title=_(u"Content panel title"),
        required=True,
    )
    klass = schema.TextLine(
        title=_(u"CSS Class"),
        required=False,
    )
    headline = schema.TextLine(
        title=_(u"Headline"),
        required=False,
    )
    abstract = schema.Text(
        title=_(u"Abstract"),
        description=_(u"Short and visualy highlighted teaser message"),
        required=False,
    )


class BasePanel(Item):
    grok.implements(IBasePanel)
    pass


class View(grok.View):
    grok.context(IBasePanel)
    grok.require('zope2.View')
    grok.name('view')

    def render_item(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@content-view')()
        return template


class ContentView(grok.View):
    grok.context(IBasePanel)
    grok.require('zope2.View')
    grok.name('content-view')
