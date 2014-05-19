from Acquisition import aq_inner
from five import grok
from zope import schema

from plone.dexterity.content import Item

from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable

from ade25.panelpage import MessageFactory as _


class IImagePanel(form.Schema, IImageScaleTraversable):
    """
    A single image panel
    """
    title = schema.TextLine(
        title=_(u"Content panel title"),
        required=True,
    )
    klass = schema.TextLine(
        title=_(u"CSS Class"),
        required=False,
    )
    image = NamedBlobImage(
        title=_(u"Panel Icon Image"),
        description=_(u"Upload panel icon image suitable in size and "
                      u"dimension for the usecase"),
        required=False,
    )
    caption = schema.Text(
        title=_(u"Caption"),
        description=_(u"Enter optional image caption text"),
        required=False,
    )


class ImagePanel(Item):
    grok.implements(IImagePanel)
    pass


class View(grok.View):
    grok.context(IImagePanel)
    grok.require('zope2.View')
    grok.name('view')

    def render_item(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@content-view')()
        return template


class ContentView(grok.View):
    grok.context(IImagePanel)
    grok.require('zope2.View')
    grok.name('content-view')
