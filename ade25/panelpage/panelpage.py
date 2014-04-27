import json
from Acquisition import aq_inner
from AccessControl import Unauthorized
from five import grok
from plone import api

from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.lifecycleevent import modified
from plone.keyring import django_random

from Products.CMFPlone.utils import safe_unicode
from zope.publisher.interfaces import IPublishTraverse
from plone.app.layout.viewlets.interfaces import IBelowContentBody

from Products.CMFCore.interfaces import IContentish

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
        context = aq_inner(self.context)
        self.has_subcontent = self.has_stored_layout()
        self.errors = {}
        unwanted = ('_authenticator', 'form.button.Submit')
        required = ('title')
        if 'form.button.Submit' in self.request:
            authenticator = getMultiAdapter((context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            form = self.request.form
            form_data = {}
            form_errors = {}
            errorIdx = 0
            for value in form:
                if value not in unwanted:
                    form_data[value] = safe_unicode(form[value])
                    if not form[value] and value in required:
                        error = {}
                        error['active'] = True
                        error['msg'] = _(u"This field is required")
                        form_errors[value] = error
                        errorIdx += 1
                    else:
                        error = {}
                        error['active'] = False
                        error['msg'] = form[value]
                        form_errors[value] = error
            if errorIdx > 0:
                self.errors = form_errors
            else:
                self._create_panel(form)

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

    def default_value(self, error):
        value = ''
        if error['active'] is False:
            value = error['msg']
        return value

    def _create_panel(self, data):
        context = aq_inner(self.context)
        new_title = data['title']
        token = django_random.get_random_string(length=12)
        api.content.create(
            type='ade25.panelpage.contentblock',
            id=token,
            title=new_title,
            container=context,
            safe_id=True
        )
        url = context.absolute_url()
        return self.request.response.redirect(url)


class PanelPageEditor(grok.View):
    grok.context(IPanelPage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('panelpage-editor')

    def update(self):
        self.has_subcontent = len(self.contained_blocks()) > 0

    def render_item(self, uid):
        item = api.content.get(UID=uid)
        template = item.restrictedTraverse('@@content-view')()
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

    def get_component_icon(self, component):
        matrix = {
            'base': 'ion-document',
            'text': 'ion-document-text',
            'image': 'ion-image',
            'listing': 'ion-ios7-albums-outline',
            'box': 'ion-filing',
            'alias': 'ion-ios7-download',
            'placeholder': 'ion-ios7-circle-outline'
        }
        return matrix[component]

    def rendered_panelgrid(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@panelgrid')()
        return template

    def rendered_panel(self, uid):
        context = aq_inner(self.context)
        item = api.content.get(UID=uid)
        if item:
            template = item.restrictedTraverse('@@content-view')()
        else:
            template = context.restrictedTraverse('@@panel-error')()
        return template


class PanelPageBlocks(grok.View):
    """ Generic router for panel page content blocks

        :param action:  CRUD content action
        :param uid:     Content block UID
    """
    grok.context(IPanelPage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('ppb')

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
        new_title = self.request.form.get('title', token)
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
                    'klass': 'panel-column'
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


class PanelError(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('panel-error')

    def update(self):
        self.uuid = self.request.get('uuid', '')


class RearrangeBlocks(grok.View):
    grok.context(IPanelPage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('rearrange-panelpage')

    def update(self):
        self.query = self.request["QUERY_STRING"]

    def render(self):
        context = aq_inner(self.context)
        sort_query = list(self.query.split('&'))
        layout_order = list()
        for x in sort_query:
            details = x.split('=')
            key = int(details[0])
            value = details[1]
            layout_order.insert(key, value)
        setattr(context, 'panelPageLayout', layout_order)
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
