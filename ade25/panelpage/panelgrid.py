import json
from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from plone import api
from plone.keyring import django_random
from zope.lifecycleevent import modified

from ade25.panelpage.panelpage import IPanelPage


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
        stored = getattr(context, 'panelPageLayout')
        return stored

    def gridrow(self):
        grid = self.stored_layout()
        block_id = self.traverse_subpath[0]
        return grid[int(block_id)]

    def panels(self):
        return self.gridrow()['panels']

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
    grok.context(IPanelPage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('gridcolumn')

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
        idx = self.traverse_subpath[1]
        updated = self.stored_layout()
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

    def _create_panel(self, data):
        context = aq_inner(self.context)
        new_title = data['title']
        token = django_random.get_random_string(length=12)
        api.content.create(
            type='ade25.panelpage.contentpanel',
            id=token,
            title=new_title,
            container=context,
            safe_id=True
        )
        url = context.absolute_url()
        return self.request.response.redirect(url)
