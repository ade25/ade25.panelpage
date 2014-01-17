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


# Interface class; used to define content-type schema.

class IPage(form.Schema, IImageScaleTraversable):
    """
    A modular ppage with panel layout
    """


class Page(Container):
    grok.implements(IPage)

    # Add your class methods and properties here
    pass


class View(grok.View):
    grok.context(IPage)
    grok.require('zope2.View')
    grok.name('view')
