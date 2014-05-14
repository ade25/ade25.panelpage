from Acquisition import aq_inner
from five import grok
from zope import schema

from plone.dexterity.content import Item

from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable

from ade25.panelpage import MessageFactory as _


class IPanel(form.Schema, IImageScaleTraversable):
    """
    A single content panel or box
    """
    title = schema.TextLine(
        title=_(u"Content Panel Title"),
        required=True,
    )
    klass = schema.TextLine(
        title=_(u"CSS Class"),
        required=False,
    )
    form.omitted('component')
    component = schema.TextLine(
        title=_(u"Component"),
        required=False,
    )


class Panel(Item):
    grok.implements(IPanel)
    pass


class View(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('view')

    def render_item(self):
        context = aq_inner(self.context)
        component = getattr(context, 'component')
        viewname = '@@panel-{0}'.format(component)
        template = context.restrictedTraverse(viewname)()
        return template


class ContentView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('content-view')


class HeadingView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('panel-heading')


class SubheadingView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('panel-subheading')


class AbstractView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('panel-abstract')


class TextView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('panel-text')


class RichTextView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('panel-richtext')


class ImageView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('panel-image')
