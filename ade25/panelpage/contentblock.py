from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from plone import api
from zope import schema
from plone.dexterity.content import Container

from plone.directives import form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from ade25.panelpage.page import IPage

from ade25.panelpage import MessageFactory as _


class IContentBlock(form.Schema, IImageScaleTraversable):
    """
    A single content block for layout composition
    """
    title = schema.TextLine(
        title=_(u"Content panel title"),
        required=True,
    )
    headline = schema.TextLine(
        title=_(u"Content Block Headline"),
        description=_(u"Optional headline for this block"),
        required=False,
    )
    description = schema.Text(
        title=_(u"Teaser"),
        description=_(u"Short and visualy highlighted teaser message"),
        required=False,
    )
    text = RichText(
        title=_(u"Block Body Text"),
        required=False,
    )
    image = NamedBlobImage(
        title=_(u"Image"),
        required=False,
    )
    imageRight = schema.Bool(
        title=_(u"Right align image"),
        description=_(u"Change the default image position to the right third"),
        required=False,
    )
    panels = schema.List(
        title=_(u"Associated Content Panels"),
        description=_(u"A list of content panel identifiers that will be "
                      u"automatically updated. Normally you do not need to "
                      u"change this list"),
        value_type=schema.TextLine(
            title=_(u"Panel UID"),
        ),
        required=False,
    )
    panelPageLayout = schema.Text(
        title=u"Panel Page Layout",
        required=False,
    )


@grok.subscribe(IContentBlock, IObjectModifiedEvent)
def reindex_container(obj, event):
    parent = aq_parent(aq_inner(obj))
    if not IPage.providedBy(parent):
        return
    catalog = api.portal.get_tool(name='portal_catalog')
    parent_path = '/'.join(parent.getPhysicalPath())
    if catalog.getrid(parent_path) is not None:
        parent.reindexObject()


class ContentBlock(Container):
    grok.implements(IContentBlock)
    pass


class View(grok.View):
    grok.context(IContentBlock)
    grok.require('zope2.View')
    grok.name('view')

    def render_item(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@content-view')()
        return template


class ContentView(grok.View):
    grok.context(IContentBlock)
    grok.require('zope2.View')
    grok.name('content-view')

    def asignment_context(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        return parent.absolute_url()

    def is_editable(self):
        return not api.user.is_anonymous()

    def has_data(self):
        context = aq_inner(self.context)
        has_content = False
        if (context.text or context.Description() or context.panels):
            has_content = True
        return has_content

    def computed_klass(self):
        klass = 'app-contentblock-default'
        if not api.user.is_anonymous():
            state = self.item_state_info()
            state_klass = ('app-contentblock-{0}').format(state)
            klass = state_klass + ' app-contentblock-editable'
        return klass

    def item_state_info(self):
        context = aq_inner(self.context)
        return api.content.get_state(obj=context)

    def render_item(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@panelgrid')()
        return template


class PanelGrid(grok.View):
    grok.context(IContentBlock)
    grok.require('zope2.View')
    grok.name('panelgrid')

    def update(self):
        self.display_panelgrid = self.panel_idx() > 1

    def asignment_context(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        return parent.absolute_url()

    def has_panels(self):
        context = aq_inner(self.context)
        return context.panels is not None

    def panel_idx(self):
        idx = 0
        if self.has_panels():
            idx = len(self.asigned_panels())
        return idx

    def first_panel(self):
        return self.asigned_panels()[0]

    def asigned_panels(self):
        context = aq_inner(self.context)
        return getattr(context, 'panels', '')

    def rendered_panel(self, uid):
        context = aq_inner(self.context)
        item = api.content.get(UID=uid)
        if item:
            template = item.restrictedTraverse('@@basic-content-view')()
        else:
            template = context.restrictedTraverse('@@panel-error')()
        return template

    def is_editable(self):
        return not api.user.is_anonymous()

    def computed_klass(self):
        base_klass = 'col-xs-12 col-sm-'
        vocab = ['3', '6', '4', '3']
        key = self.panel_idx()
        col_klass = vocab[key - 1]
        return base_klass + col_klass

    def item_state_info(self):
        context = aq_inner(self.context)
        return api.content.get_state(obj=context)

    def klass_matrix(self):
        matrix = {
            '2': 'col-sm-6',
            '3': 'col-sm-4',
            '4': 'col-sm-3'
        }
        return matrix
