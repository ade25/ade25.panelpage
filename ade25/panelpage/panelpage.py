import json
from Acquisition import aq_inner
from five import grok
from plone import api

from zope.interface import Interface
from zope.lifecycleevent import modified

from zope.publisher.interfaces import IPublishTraverse
from plone.app.layout.viewlets.interfaces import IBelowContentBody

from Products.CMFCore.interfaces import IContentish

from ade25.panelpage.config import panel_components
from ade25.panelpage.config import pretty_components
from ade25.panelpage.config import component_icons

from ade25.panelpage import MessageFactory as _


class IPanelPage(Interface):
    """ Marker for panel and block enabled content """


class PanelPageView(grok.View):
    grok.context(IPanelPage)
    grok.require('zope2.View')
    grok.name('panelpage-view')

    def panelpage(self):
        context = aq_inner(self.context)
        tmpl = context.restrictedTraverse('@@panelpage')()
        return tmpl


class PanelPageViewlet(grok.Viewlet):
    grok.context(IPanelPage)
    grok.viewletmanager(IBelowContentBody)
    grok.require('zope2.View')
    grok.name('ade25.panelpage.PanelPageViewlet')

    def panelpage(self):
        context = aq_inner(self.context)
        tmpl = context.restrictedTraverse('@@panelpage')()
        return tmpl


class PanelPage(grok.View):
    grok.context(IPanelPage)
    grok.require('zope2.View')
    grok.name('panelpage')

    def update(self):
        self.has_subcontent = self.has_stored_layout()

    def is_editable(self):
        editable = False
        if not api.user.is_anonymous():
                editable = True
        return editable

    def rendered_panelgrid(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@panelgrid')()
        return template

    def render_item(self, uid):
        item = api.content.get(UID=uid)
        template = item.restrictedTraverse('@@panelgrid')()
        return template

    def computed_klass(self):
        klass = 'app-panelpage-default'
        if self.is_editable():
            klass = 'app-panelpage-editable'
        return klass

    def has_stored_layout(self):
        context = aq_inner(self.context)
        stored = getattr(context, 'panelPageLayout')
        if stored is not None:
            return True
        return False

    def contained_blocks(self):
        context = aq_inner(self.context)
        block_layout = getattr(context, 'panelPageLayout', None)
        if block_layout is None:
            return list()
        else:
            return block_layout


class PanelPageEditor(grok.View):
    grok.context(IPanelPage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('panelpage-editor')

    def update(self):
        self.has_subcontent = len(self.contained_blocks()) > 0

    def render_item(self, uid):
        item = api.content.get(UID=uid)
        component = getattr(item, 'component')
        viewname = '@@panel-{0}'.format(component)
        template = item.restrictedTraverse(viewname)()
        return template

    def computed_klass(self):
        klass = 'app-panelpage-default'
        if self.is_editable():
            klass = 'app-panelpage-editable'
        return klass

    def item_state_klass(self, state):
        return ('ppe-block-{0}').format(state)

    def item_state_info(self, uid):
        item = api.content.get(UID=uid)
        state = api.content.get_state(obj=item)
        return state

    def available_transitions(self, state):
        transitions = {
            'published': 'retract',
            'visible': 'hide',
            'hidden': 'show',
            'private': 'publish'
        }
        return transitions[state]

    def contained_blocks(self):
        context = aq_inner(self.context)
        block_layout = getattr(context, 'panelPageLayout', None)
        if block_layout is None:
            return list()
        else:
            return block_layout

    def panels(self, row_idx):
        grid = self.contained_blocks()
        row = grid[int(row_idx)]
        return row['panels']

    def prettify_name(self, component):
        names = pretty_components()
        return names[component]

    def is_editable(self):
        editable = False
        if not api.user.is_anonymous():
                editable = True
        return editable

    def default_value(self, error):
        value = ''
        if error['active'] is False:
            value = error['msg']
        return value


class PanelBlockEditor(grok.View):
    grok.context(IPanelPage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('panelblock-editor')

    def update(self):
        self.has_layout = len(self.stored_layout()) > 0
        self.block_id = self.traverse_subpath[0]

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    def stored_layout(self):
        context = aq_inner(self.context)
        block_layout = getattr(context, 'panelPageLayout', None)
        if block_layout is None:
            return list()
        else:
            return block_layout

    def gridrow(self):
        grid = self.stored_layout()
        return grid[int(self.block_id)]

    def panels(self):
        return self.gridrow()['panels']

    def show_panel_obj(self, uuid):
        if uuid is None:
            return False
        return True

    def get_started(self):
        display = False
        panels = self.panels()
        if panels == 0:
            display = True
        if panels == 1 and panels[0]['component'] == 'placeholder':
            display = True
        return display

    def must_setup_panel(self, component):
        display = False
        if component == 'placeholder':
            display = True
        return display

    def show_ratio_selection(self):
        return len(self.panels()) == 2

    def active_ratio(self):
        panel = self.panels()[0]
        value = panel['grid-col']
        return value

    def available_components(self):
        return panel_components()

    def prettify_name(self, component):
        names = pretty_components()
        return names[component]

    def get_component_icon(self, component):
        matrix = component_icons()
        return matrix[component]

    def rendered_panelgrid(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@panelgrid')()
        return template

    def rendered_panel(self, uid):
        context = aq_inner(self.context)
        item = api.content.get(UID=uid)
        if item:
            component = getattr(item, 'component')
            viewname = '@@panel-{0}'.format(component)
            template = item.restrictedTraverse(viewname)()
        else:
            template = context.restrictedTraverse('@@panel-error')()
        return template


class PanelPageBlocks(grok.View):
    """ Generic router for panel content """
    grok.context(IPanelPage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('panel-editor')

    def render(self):
        context = aq_inner(self.context)
        base_url = context.absolute_url()
        row = self.traverse_subpath[0]
        panel = self.traverse_subpath[1]
        component = self.traverse_subpath[2]
        uuid = self.traverse_subpath[3]
        url = '{0}/@@panel-{1}/{2}/{3}/{4}'.format(
            base_url, component, row, panel, uuid)
        return self.request.response.redirect(url)

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self


class PanelError(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('panel-error')

    def update(self):
        self.row_idx = self.subpath[0]

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self


class RearrangeBlocks(grok.View):
    grok.context(IPanelPage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('rearrange-panelpage')

    def update(self):
        self.query = self.request["QUERY_STRING"]

    def render(self):
        context = aq_inner(self.context)
        grid = getattr(context, 'panelPageLayout')
        sort_query = list(self.query.split('&'))
        layout_order = list()
        for x in sort_query:
            details = x.split('=')
            key = int(details[0])
            value = grid[key]
            layout_order.insert(key, value)
        setattr(context, 'panelPageLayout', layout_order)
        modified(context)
        context.reindexObject(idxs='modified')
        msg = _(u"Panelpage order successfully updated")
        results = {'success': True,
                   'message': msg
                   }
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return json.dumps(results)


class TransitionState(grok.View):
    grok.context(IContentish)
    grok.implements(IPublishTraverse)
    grok.require('cmf.ModifyPortalContent')
    grok.name('transition-state')

    def render(self):
        context = aq_inner(self.context)
        uuid = self.traverse_subpath[0]
        item = api.content.get(UID=uuid)
        if len(self.traverse_subpath) > 1:
            state = self.traverse_subpath[1]
        else:
            state = api.content.get_state(obj=item)
        transitions = self.available_transitions()
        action = transitions[state]
        api.content.transition(obj=item, transition=action)
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

    def available_transitions(self):
        transitions = {
            'published': 'retract',
            'private': 'publish'
        }
        return transitions
