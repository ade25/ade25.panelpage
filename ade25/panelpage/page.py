from Acquisition import aq_inner
from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.indexer import indexer
from plone.dexterity.content import Container

from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder


from ade25.panelpage import MessageFactory as _


class IPage(form.Schema, IImageScaleTraversable):
    """
    A modular ppage with panel layout
    """
    headline = schema.TextLine(
        title=_(u"Headline"),
        description=_(u"Optional headline overiding the default title in the "
                      u"content page view"),
        required=False,
    )
    abstract = schema.Text(
        title=_(u"Abstract"),
        description=_(u"Optional abstract for the page content overriding the "
                      u"Dublin Core description"),
        required=False,
    )
    text = RichText(
        title=_(u"Body Text"),
        description=_(u"Optional rich body text. Note: you can use content "
                      u"blocks to structure the page body"),
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
