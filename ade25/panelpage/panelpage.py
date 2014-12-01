# -*- coding: UTF-8 -*-
"""Module that provides functionality for modular layout management."""

from Acquisition import aq_inner
from Products.CMFCore.interfaces import IContentish
from ade25.panelpage import MessageFactory as _
from ade25.panelpage.config import component_icons
from ade25.panelpage.config import panel_components
from ade25.panelpage.config import pretty_components
from five import grok
from plone import api
from plone.app.layout.viewlets.interfaces import IBelowContentBody
from zope.interface import Interface
from zope.lifecycleevent import modified

import json


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
        self.has_content = self.has_stored_layout()

    def is_editable(self):
        editable = False
        if not api.user.is_anonymous():
                editable = True
        return editable

    def rendered_panelgrid(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@panelgrid')()
        return template

    def computed_klass(self):
        klass = 'app-panelpage-default'
        if self.is_editable():
            klass = 'app-panelpage-editable'
        return klass

    def has_stored_layout(self):
        context = aq_inner(self.context)
        if hasattr(context.aq_explicit, 'panelPageLayout'):
            stored = getattr(context, 'panelPageLayout')
            if stored is not None:
                return True
        return False


class PanelPageEditor(grok.View):
    grok.context(IPanelPage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('panelpage-editor')

    def update(self):
        self.has_content = len(self.stored_layout()) > 0

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

    def stored_layout(self):
        context = aq_inner(self.context)
        block_layout = getattr(context.aq_explicit, 'panelPageLayout', None)
        if block_layout is None:
            return list()
        else:
            return block_layout

    def panels(self, row_idx):
        grid = self.stored_layout()
        row = grid[int(row_idx)]
        return row['panels']

    def prettify_name(self, component):
        names = pretty_components()
        if component == 'placeholder':
            return _(u"Unconfigured")
        else:
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
        self.portal_url = api.portal.get().absolute_url()

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
            layout_order.append(value)
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
