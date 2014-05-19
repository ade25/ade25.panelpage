from Acquisition import aq_inner
from five import grok
from zope import schema

from plone.dexterity.content import Container

from plone.directives import form
from plone.app.textfield import RichText
from plone.namedfile.interfaces import IImageScaleTraversable

from ade25.panelpage import MessageFactory as _


class ITextPanel(form.Schema, IImageScaleTraversable):
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
    text = RichText(
        title=_(u"Body Text"),
        description=_(u"Please enter rich formatted text. But keep it short "
                      u"and suitable for a content panel"),
        required=False,
    )


class TextPanel(Container):
    grok.implements(ITextPanel)
    pass


class View(grok.View):
    grok.context(ITextPanel)
    grok.require('zope2.View')
    grok.name('view')

    def render_item(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@content-view')()
        return template


class ContentView(grok.View):
    grok.context(ITextPanel)
    grok.require('zope2.View')
    grok.name('content-view')
