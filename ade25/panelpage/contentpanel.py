from Acquisition import aq_inner
from five import grok
from plone import api
from zope import schema

from plone.dexterity.content import Container

from plone.directives import form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable

from z3c.relationfield.schema import RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.app.uuid.utils import uuidToObject

from ade25.panelpage import MessageFactory as _


class IContentPanel(form.Schema, IImageScaleTraversable):
    """
    A single content panel or box
    """
    title = schema.TextLine(
        title=_(u"Content panel title"),
        required=True,
    )
    description = schema.Text(
        title=_(u"Teaser"),
        description=_(u"Short and visualy highlighted teaser message"),
        required=False,
    )
    image = NamedBlobImage(
        title=_(u"Panel Icon Image"),
        description=_(u"Upload panel icon image suitable in size and "
                      u"dimension for the usecase"),
        required=False,
    )
    icon_klass = schema.TextLine(
        title=_(u"Content panel icon class"),
        description=_(u"Add an icon class from font awesome site"),
        required=False,
    )
    text = RichText(
        title=_(u"Body Text"),
        description=_(u"Please enter rich formatted text. But keep it short "
                      u"and suitable for a content panel"),
        required=False,
    )
    linked_item = schema.TextLine(
        title=_(u"Linked content item"),
        description=_(u"This field will be populated with an uid by the "
                      u"system. Do not edit it yourself"),
        required=False,
    )
    show_contentlisting = schema.Bool(
        title=_(u"Enable content listing"),
        description=_(u"List contents of link target"),
        required=False
    )


class ContentPanel(Container):
    grok.implements(IContentPanel)
    pass


class View(grok.View):
    grok.context(IContentPanel)
    grok.require('zope2.View')
    grok.name('view')

    def render_item(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@content-view')()
        return template


class ContentView(grok.View):
    grok.context(IContentPanel)
    grok.require('zope2.View')
    grok.name('content-view')

    def is_editable(self):
        editable = False
        if not api.user.is_anonymous():
                editable = True
        return editable

    def has_icon(self):
        context = aq_inner(self.context)
        has_icon = False
        if context.icon_klass or context.image:
            has_icon = True
        return has_icon

    def computed_klass(self):
        klass = 'app-contentblock-default'
        if not api.user.is_anonymous():
            klass = klass + ' app-contentblock-editable'
        return klass

    def item_state_info(self):
        context = aq_inner(self.context)
        return api.content.get_state(obj=context)

    def generate_contentlisting(self):
        item = self.resolve_linked_item()
        data = item.restrictedTraverse('@@folderListing')(
            portal_type=['ade25.panelpage.contentpage'])
        return data

    def resolve_linked_item(self):
        context = aq_inner(self.context)
        uuid = getattr(context, 'linked_item', None)
        obj = uuidToObject(uuid)
        return obj

    def render_item_content(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@basic-content-view')()
        return template


class BasicContentView(grok.View):
    grok.context(IContentPanel)
    grok.require('zope2.View')
    grok.name('basic-content-view')

    def is_editable(self):
        editable = False
        if not api.user.is_anonymous():
                editable = True
        return editable

    def has_icon(self):
        context = aq_inner(self.context)
        has_icon = False
        if context.icon_klass or context.image:
            has_icon = True
        return has_icon

    def height_adjustable(self):
        context = aq_inner(self.context)
        context_id = context.getId()
        adjustable = True
        if context_id == 'panel-manager':
            adjustable = False
        return adjustable

    def computed_klass(self):
        klass = 'app-contentblock-default'
        if not api.user.is_anonymous():
            klass = klass + ' app-contentblock-editable'
        return klass

    def item_state_info(self):
        context = aq_inner(self.context)
        return api.content.get_state(obj=context)

    def generate_contentlisting(self):
        item = self.resolve_linked_item()
        data = item.restrictedTraverse('@@folderListing')(
            portal_type=['ade25.panelpage.contentpage'])
        return data

    def resolve_linked_item(self):
        context = aq_inner(self.context)
        uuid = getattr(context, 'linked_item', None)
        obj = uuidToObject(uuid)
        return obj
