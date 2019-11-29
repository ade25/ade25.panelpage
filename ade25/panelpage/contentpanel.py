from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from plone import api
from plone.supermodel import model
from zope import schema

from plone.dexterity.content import Container

from plone.autoform import directives, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable

from plone.formwidget.querystring.widget import QueryStringFieldWidget
from plone.app.uuid.utils import uuidToObject

from ade25.panelpage import MessageFactory as _


class IContentPanel(model.Schema, IImageScaleTraversable):
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
    subitems = schema.Bool(
        title=_(u"Display subitems"),
        description=_(u"Use this setting to automatically list all subcontents"
                      u" of this context. All custom query selections made"
                      u" will be ignored"),
        required=False
    )
    directives.widget(query=QueryStringFieldWidget)
    query = schema.List(
        title=_(u"Search terms"),
        description=_(u"Define the search terms for the items you want to list"
                      u" by choosing what to match on. The list of results"
                      u"will be dynamically updated"),
        value_type=schema.Dict(
            value_type=schema.Field(),
            key_type=schema.TextLine()
        ),
        required=False
    )
    sort_on = schema.TextLine(
        title=_(u'label_sort_on', default=u'Sort on'),
        description=_(u"Sort the collection on this index"),
        required=False,
    )

    sort_reversed = schema.Bool(
        title=_(u'label_sort_reversed', default=u'Reversed order'),
        description=_(u'Sort the results in reversed order'),
        required=False,
    )

    limit = schema.Int(
        title=_(u'Limit'),
        description=_(u'Limit Search Results'),
        required=False,
        default=1000,
    )

    item_count = schema.Int(
        title=_(u'label_item_count', default=u'Item count'),
        description=_(u'Number of items that will show up in one batch.'),
        required=False,
        default=30,
    )


class ContentPanel(Container):
    grok.implements(IContentPanel)
    pass


class View(grok.View):
    grok.context(IContentPanel)
    grok.require('zope2.View')
    grok.name('view')

    def parent_url(self):
        parent = aq_parent(aq_inner(self.context))
        return parent.absolute_url()

    def back_url(self):
        url = self.parent_url()
        if len(self.traverse_subpath()) > 0:
            row = self.traverse_subpath[0]
            url = '{0}/panelblock-editor/{1}'.format(url, row)
        return url

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

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
