from Acquisition import aq_inner
from five import grok

from zope import schema

from plone.indexer import indexer
from plone.dexterity.content import Container

from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable

from ade25.panelpage import MessageFactory as _


class IPage(form.Schema, IImageScaleTraversable):
    """
    A modular ppage with panel layout
    """
    hide_dcbasic = schema.Bool(
        title=_(u"Hide title and description"),
        description=_(u"Prevent the rendering of DC Title and Description to"
                      u"use headline and abstract of the first content block"),
        required=False,
    )


@indexer(IPage)
def childNodeIndexer(obj):
    searchable_text = obj.SearchableText()
    for item in obj.getFolderContents(
        {'portal_type': 'ade25.panelpage.contentblock'},
    ):
        searchable_text += item.SearchableText()
    return searchable_text
grok.global_adapter(childNodeIndexer, name="SearchableText")


class Page(Container):
    grok.implements(IPage)
    pass


class View(grok.View):
    grok.context(IPage)
    grok.require('zope2.View')
    grok.name('view')

    def has_abstract(self):
        context = aq_inner(self.context)
        show = False
        if context.Description or context.abstract:
            show = True
        return show
