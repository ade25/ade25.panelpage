from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

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


class Page(Container):
    grok.implements(IPage)
    pass


class View(grok.View):
    grok.context(IPage)
    grok.require('zope2.View')
    grok.name('view')
