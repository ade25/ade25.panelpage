# -*- coding: utf-8 -*-
"""Module to render and manipulate a panel layout grid"""

from AccessControl import Unauthorized
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from ade25.panelpage.panelpage import IPanelPage
from five import grok
from plone import api
from plone.keyring import django_random
from zope.component import getMultiAdapter
from zope.lifecycleevent import modified


class PanelGrid(grok.View):
    grok.context(IPanelPage)
    grok.require('zope2.View')
    grok.name('panelgrid')

    def update(self):
        self.display_panelgrid = True

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    def display_external_content(self):
        context = aq_inner(self.context)
        display = False
        if (hasattr(context, 'query') or context.contentAlias):
            display = True
        return display

    def stored_layout(self):
        context = aq_inner(self.context)
        stored = getattr(aq_base(context), 'panelPageLayout')
        return stored

    def panel_item(self, uuid):
        return api.content.get(UID=uuid)

    def show_panel_obj(self, uuid):
        if uuid is None:
            return False
        return True

    def asignment_context(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        return parent.absolute_url()

    def first_panel(self):
        return self.asigned_panels()[0]

    def asigned_panels(self):
        context = aq_inner(self.context)
        return getattr(context, 'panels', '')

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


class GridRows(grok.View):
    """ Generic router for panel page content blocks

        :param action:  CRUD content action
        :param uid:     Content block UID
    """
    grok.context(IPanelPage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('gridrow')

    def update(self):
        context = aq_inner(self.context)
        self.data = {}
        if 'form.button.Submit' in self.request:
            authenticator = getMultiAdapter((context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            self.data = self.request.form

    def render(self):
        context = aq_inner(self.context)
        action = self.traverse_subpath[0]
        next_url = context.absolute_url()
        if action == 'create':
            next_url = self._create_panel()
        if action == 'delete':
            next_url = self._delete_panel()
        if action == 'transition':
            next_url = self._transition_panel()
        return self.request.response.redirect(next_url)

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    def _create_panel(self):
        context = aq_inner(self.context)
        token = django_random.get_random_string(length=24)
        title = self.request.form.get('title')
        new_title = 'row'
        if title:
            new_title = title
        block = {
            'id': token,
            'title': new_title,
            'status': 'visible',
            'klass': 'pp-row-default',
            'panels': [
                {
                    'uuid': None,
                    'component': u"placeholder",
                    'grid-col': 12,
                    'klass': 'pp-column'
                }
            ]
        }
        items = getattr(context, 'panelPageLayout', None)
        if items is None:
            items = list()
        items.append(block)
        setattr(context, 'panelPageLayout', items)
        modified(context)
        context.reindexObject(idxs='modified')
        url = '{0}/@@panelpage-editor'.format(context.absolute_url())
        return url

    def _delete_panel(self):
        context = aq_inner(self.context)
        grid = getattr(context, 'panelPageLayout')
        idx = self.traverse_subpath[1]
        grid.pop(int(idx))
        setattr(context, 'panelPageLayout', grid)
        url = '{0}/@@panelpage-editor'.format(context.absolute_url())
        return url

    def _transition_panel(self):
        context = aq_inner(self.context)
        grid = getattr(context, 'panelPageLayout')
        index = self.traverse_subpath[1]
        idx = int(index)
        row = grid[idx]
        # check if we have an explicit transition requested
        if len(self.traverse_subpath) > 2:
            state = self.traverse_subpath[2]
        else:
            state = row['status']
        changed = 'visible'
        if state == 'visible':
            changed = 'hidden'
        row['status'] = changed
        grid[idx] = row
        setattr(context, 'panelPageLayout', grid)
        url = '{0}/@@panelpage-editor'.format(context.absolute_url())
        return url

    def available_transitions(self, state):
        transitions = {
            'published': 'retract',
            'visible': 'hide',
            'hidden': 'show',
            'private': 'publish'
        }
        return transitions[state]


class GridColumns(grok.View):
    grok.context(IPanelPage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('gridcolumn')

    def render(self):
        context = aq_inner(self.context)
        action = self.traverse_subpath[0]
        new_layout = self.stored_layout()
        if action == 'create':
            new_layout = self._create_column()
        if action == 'delete':
            new_layout = self._delete_column()
        if action == 'update':
            new_layout = self._update_column()
        if action == 'move':
            new_layout = self._move_column()
        if action == 'add':
            new_layout = self._add_content()
        setattr(context, 'panelPageLayout', new_layout)
        modified(context)
        context.reindexObject(idxs='modified')
        row = self.traverse_subpath[1]
        base_url = context.absolute_url()
        next_url = '{0}/@@panelblock-editor/{1}'.format(base_url, row)
        return self.request.response.redirect(next_url)

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
        stored = getattr(context, 'panelPageLayout')
        return stored

    def gridrow(self):
        grid = self.stored_layout()
        row = self.traverse_subpath[1]
        return grid[int(row)]

    def panels(self):
        return self.gridrow()['panels']

    def _create_column(self):
        grid = self.stored_layout()
        row_idx = self.traverse_subpath[1]
        row = grid[int(row_idx)]
        cols = self.gridrow()['panels']
        col_idx = len(cols) + 1
        col_size = 12 / col_idx
        col = {
            'uuid': None,
            'component': u"placeholder",
            'grid-col': col_size,
            'klass': 'panel-column'
        }
        # Reset col size to make room for additional column
        for x in cols:
            x['grid-col'] = col_size
        cols.append(col)
        row['panels'] = cols
        grid[int(row_idx)] = row
        return grid

    def _delete_column(self):
        row_idx = int(self.traverse_subpath[1])
        col_idx = int(self.traverse_subpath[2])
        grid = self.stored_layout()
        row = grid[row_idx]
        cols = self.gridrow()['panels']
        col = cols[col_idx]
        if col['component'] != 'placeholder':
            uuid = col['uuid']
            panel = api.content.get(UID=uuid)
            api.content.delete(obj=panel)
        cols.pop(col_idx)
        grid_idx = len(cols)
        col_size = 12 / grid_idx
        for x in cols:
            x['grid-col'] = col_size
        row['panels'] = cols
        grid[int(row_idx)] = row
        return grid

    def _update_column(self):
        updated = self.stored_layout()
        row = self.gridrow()
        panels = self.panels()
        panels[0]['grid-col'] = self.traverse_subpath[2]
        panels[1]['grid-col'] = self.traverse_subpath[3]
        row['panels'] = panels
        row_idx = int(self.traverse_subpath[1])
        updated[row_idx] = row
        return updated

    def _move_column(self):
        updated = self.current_layout()
        return updated

    def _add_content(self):
        grid = self.stored_layout()
        row_idx = self.traverse_subpath[1]
        row = grid[int(row_idx)]
        cols = self.gridrow()['panels']
        component = self.traverse_subpath[2]
        col_idx = self.traverse_subpath[3]
        col = cols[int(col_idx)]
        # Create panel content type here
        uid = self._create_panel(component)
        col['component'] = component
        col['uuid'] = uid
        col['klass'] = 'panel-column'
        row['panels'] = cols
        grid[int(row_idx)] = row
        return grid

    def _create_panel(self, component):
        context = aq_inner(self.context)
        token = django_random.get_random_string(length=24)
        item = api.content.create(
            type='ade25.panelpage.panel',
            id=token,
            title=token,
            container=context,
            safe_id=True
        )
        setattr(item, 'component', component)
        uuid = api.content.get_uuid(obj=item)
        return uuid
