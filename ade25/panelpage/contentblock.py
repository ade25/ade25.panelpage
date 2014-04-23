import json
from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from plone import api
from zope import schema
from zope.component import getMultiAdapter
from zope.lifecycleevent import modified

from plone.dexterity.content import Container

from plone.directives import form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from plone.uuid.interfaces import IUUID
from plone.namedfile.interfaces import IImageScaleTraversable
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from ade25.panelpage.page import IPage
from ade25.panelpage.blocklisting import IContentBlockListing

from ade25.panelpage import MessageFactory as _


class IContentBlock(form.Schema, IImageScaleTraversable):

    """ A single content block for layout composition. """

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
    klass = schema.TextLine(
        title=_(u"CSS Class"),
        required=False,
    )
    form.fieldset(
        'details',
        label=_(u"Block Details"),
        fields=['text', 'image', 'contentAlias']
    )
    text = RichText(
        title=_(u"Block Body Text"),
        required=False,
    )
    image = NamedBlobImage(
        title=_(u"Image"),
        required=False,
    )
    contentAlias = schema.TextLine(
        title=_(u"Content Alias/Proxy UID"),
        required=False,
    )
    form.fieldset(
        'settings',
        label=_(u"Content Block Settings"),
        fields=['contentBlockLayout']
    )
    contentBlockLayout = schema.TextLine(
        title=u"Content Block Layout",
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

    def update(self):
        self.query = self._get_query()
        if self.request.get_header('X-PJAX'):
            return '<p>This is a pjax response</p>'

    def parent_info(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        info = {}
        info['url'] = parent.absolute_url()
        info['title'] = parent.Title()
        return info

    def dynamic_contents(self, batch=True, b_start=0, b_size=None,
                         sort_on=None, limit=None, brains=False):
        context = aq_inner(self.context)
        querybuilder = getMultiAdapter((self.context, self.context.REQUEST),
                                       name='querybuilderresults')
        sort_order = 'reverse' if context.sort_reversed else 'ascending'
        if not b_size:
            b_size = context.item_count
        if not sort_on:
            sort_on = context.sort_on
        if not limit:
            limit = context.limit

        query = self.query
        if query:
            has_path_criteria = any(
                (criteria['i'] == 'path')
                for criteria in query
            )
            if not has_path_criteria:
                # Make a copy of the query to avoid modifying it
                query = list(self.query)
                query.append({
                    'i': 'path',
                    'o': 'plone.app.querystring.operation.string.path',
                    'v': '/',
                })

        return querybuilder(
            query=query, batch=batch, b_start=b_start, b_size=b_size,
            sort_on=sort_on, sort_order=sort_order,
            limit=limit, brains=brains
        )

    def _get_query(self):
        context = aq_inner(self.context)
        stored_query = getattr(context, 'query', None)
        return stored_query

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

    def show_editbar(self):
        editor = False
        context_state = getMultiAdapter((self.context, self.request),
                                        name='plone_context_state')
        current_url = context_state.current_page_url()
        if current_url.endswith('panelpage-editor'):
            editor = True
        if IPage.providedBy(aq_inner(self.context)):
            editor = False
        return editor

    def stored_layout(self):
        context = aq_inner(self.context)
        stored = getattr(context, 'contentBlockLayout')
        if stored is not None:
            return json.loads(stored)
        return list()

    def show_ratio_selection(self):
        return len(self.stored_layout()) == 2

    def active_ratio(self):
        layout = self.stored_layout()
        value = '6'
        if len(layout) > 0:
            first_col = layout[0]
            value = first_col['grid-col']
        return value

    def has_data(self):
        for panel in self.stored_layout():
            component = panel['component']
            if component != 'placeholder':
                return True
        return True

    def has_query_results(self):
        pass

    def query_results(self, **kwargs):
        context = aq_inner(self.context)
        wrapped = IContentBlockListing(context)
        return wrapped.results(**kwargs)

    def computed_klass(self):
        klass = 'app-contentblock-default'
        if not api.user.is_anonymous():
            state = self.item_state_info()
            state_klass = ('ppe-block-{0}').format(state)
            klass = state_klass + ' app-contentblock-editable'
        return klass

    def item_state_info(self):
        context = aq_inner(self.context)
        return api.content.get_state(obj=context)

    def column_edit_action(self, component):
        context = aq_inner(self.context)
        base_url = context.absolute_url()
        matrix = {
            'text': '@@edit-block-body',
            'image': '@@edit-block-image',
            'listing': '@@edit-block',
            'box': '@@edit-block',
            'alias': '@@edit-block',
            'placeholder': 'fa-ellipsis-h'
        }
        return '{0}/{1}'.format(base_url, matrix[component])

    def get_component_icon(self, component):
        matrix = {
            'text': 'fa-file-text-o',
            'image': 'fa-picture-o',
            'listing': 'fa-list',
            'box': 'fa-list-alt',
            'alias': 'fa-copy',
            'placeholder': 'fa-ellipsis-h'
        }
        return matrix[component]

    def get_started(self, component):
        display = False
        if component == 'placeholder':
            display = True
        return display

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

    def display_external_content(self):
        context = aq_inner(self.context)
        display = False
        if (hasattr(context, 'query') or context.contentAlias):
            display = True
        return display

    def stored_layout(self):
        context = aq_inner(self.context)
        stored = getattr(context, 'contentBlockLayout')
        return json.loads(stored)

    def panel_item(self, uuid):
        return api.content.get(UID=uuid)

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


class GridColumns(grok.View):
    grok.context(IContentBlock)
    grok.require('cmf.ModifyPortalContent')
    grok.name('gridcol')

    def render(self):
        context = aq_inner(self.context)
        action = self.traverse_subpath[0]
        new_layout = self.current_layout()
        if action == 'create':
            new_layout = self._create_column()
        if action == 'delete':
            new_layout = self._delete_column()
        if action == 'move':
            new_layout = self._move_column()
        if action == 'add':
            new_layout = self._add_content()
        setattr(context, 'contentBlockLayout', json.dumps(new_layout))
        modified(context)
        context.reindexObject(idxs='modified')
        next_url = context.absolute_url()
        return self.request.response.redirect(next_url)

    def old_render(self):
        context = aq_inner(self.context)
        stored = getattr(context, 'contentBlockLayout')
        layout = json.loads(stored)
        for idx, key in enumerate(self.traverse_subpath):
            item = layout[idx]
            item['grid-col'] = key
        setattr(context, 'contentBlockLayout', json.dumps(layout))
        modified(context)
        context.reindexObject(idxs='modified')
        next_url = context.absolute_url()
        return self.request.response.redirect(next_url)

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    def current_layout(self):
        context = aq_inner(self.context)
        stored = getattr(context, 'contentBlockLayout')
        return json.loads(stored)

    def _create_column(self):
        context = aq_inner(self.context)
        uid = IUUID(context)
        updated = self.current_layout()
        grid_idx = len(updated) + 1
        col_size = 12 / grid_idx
        col = {
            'uuid': uid,
            'component': u"placeholder",
            'grid-col': col_size,
            'klass': 'panel-column'
        }
        # Reset col size to make room for additional column
        for x in updated:
            x['grid-col'] = col_size
        updated.append(col)
        return updated

    def _delete_column(self):
        idx = self.traverse_subpath[1]
        updated = self.current_layout()
        updated.pop(int(idx))
        grid_idx = len(updated)
        col_size = 12 / grid_idx
        for x in updated:
            x['grid-col'] = col_size
        return updated

    def _move_column(self):
        updated = self.current_layout()
        return updated

    def _add_content(self):
        idx = int(self.traverse_subpath[1])
        col_content = self.traverse_subpath[2]
        updated = self.current_layout()
        column = updated[idx]
        column['component'] = col_content
        return updated


class RatioSelection(grok.View):
    grok.context(IContentBlock)
    grok.require('cmf.ModifyPortalContent')
    grok.name('ratio-selection')

    def render(self):
        context = aq_inner(self.context)
        stored = getattr(context, 'contentBlockLayout')
        layout = json.loads(stored)
        for idx, key in enumerate(self.traverse_subpath):
            item = layout[idx]
            item['grid-col'] = key
        setattr(context, 'contentBlockLayout', json.dumps(layout))
        modified(item)
        context.reindexObject(idxs='modified')
        next_url = context.absolute_url()
        return self.request.response.redirect(next_url)

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self
