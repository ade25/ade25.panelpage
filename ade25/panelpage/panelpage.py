from Acquisition import aq_inner
from AccessControl import Unauthorized
from five import grok
from plone import api

from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.lifecycleevent import modified
from plone.keyring import django_random

from Products.CMFPlone.utils import safe_unicode
from plone.app.uuid.utils import uuidToObject

from plone.app.layout.viewlets.interfaces import IBelowContentBody

from Products.CMFCore.interfaces import IContentish
from ade25.panelpage.contentblock import IContentBlock
from ade25.panelpage.contentpanel import IContentPanel

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
        self.has_subcontent = len(self.contained_blocks()) > 0
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

    def render_item(self, uid):
        item = api.content.get(UID=uid)
        template = item.restrictedTraverse('@@content-view')()
        return template

    def computed_klass(self):
        klass = 'app-panelpage-default'
        if self.is_editable():
            klass = 'app-panelpage-editable'
        return klass

    def contained_blocks(self):
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IContentBlock.__identifier__,
                        path=dict(query='/'.join(context.getPhysicalPath()),
                                  depth=1),
                        sort_on='getObjPositionInParent')
        return items

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
        context = aq_inner(self.context)
        self.has_subcontent = len(self.contained_blocks()) > 0
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
        url = context.absolute_url() + '/@@panelpage-editor'
        return self.request.response.redirect(url)

    def render_item(self, uid):
        item = api.content.get(UID=uid)
        template = item.restrictedTraverse('@@content-view')()
        return template

    def computed_klass(self):
        klass = 'app-panelpage-default'
        if self.is_editable():
            klass = 'app-panelpage-editable'
        return klass

    def contained_blocks(self):
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IContentBlock.__identifier__,
                        path=dict(query='/'.join(context.getPhysicalPath()),
                                  depth=1),
                        sort_on='getObjPositionInParent')
        return items


class CreateBlock(grok.View):
    grok.context(IPanelPage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('create-block')

    def update(self):
        context = aq_inner(self.context)
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

    def default_value(self, error):
        value = ''
        if error['active'] is False:
            value = error['msg']
        return value

    def _create_panel(self, data):
        context = aq_inner(self.context)
        new_title = data['title']
        token = django_random.get_random_string(length=12)
        item = api.content.create(
            type='ade25.panelpage.contentblock',
            id=token,
            title=new_title,
            container=context,
            safe_id=True
        )
        uuid = api.content.get_uuid(obj=item)
        url = context.absolute_url()
        base_url = url + '/@@setup-block?uuid=' + uuid
        next_url = base_url + '&token=' + token
        return self.request.response.redirect(next_url)


class PanelAsignment(grok.View):
    grok.context(IPanelPage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('panel-asignment')

    def update(self):
        self.uuid = self.request.get('uuid', '')

    def default_value(self, error):
        value = ''
        if error['active'] is False:
            value = error['msg']
        return value

    def rendered_item(self, uid):
        item = api.content.get(UID=uid)
        template = item.restrictedTraverse('@@content-view')()
        return template

    def render_panelgrid(self):
        item = self.resolve_item()
        template = item.restrictedTraverse('@@panelgrid')()
        return template

    def is_activated_slot(self, idx):
        return idx <= self.asigned_panels()

    def has_panels(self):
        return self.asigned_panels() > 0

    def panels(self):
        item = self.resolve_item()
        return item.panels

    def asigned_panels(self):
        item = self.resolve_item()
        count = 0
        if item.panels:
            count = len(item.panels)
        return count

    def get_asigned_panel(self, uid):
        item = api.content.get(UID=uid)
        return item.Title()

    def resolve_item(self):
        uuid = self.request.get('uuid', None)
        return uuidToObject(uuid)

    def available_panels(self):
        portal = api.portal.get()
        manager = portal['panel-manager']
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IContentPanel.__identifier__,
                        path=dict(query='/'.join(manager.getPhysicalPath()),
                                  depth=1),
                        sort_on='getObjPositionInParent')
        return items


class CreateAsignment(grok.View):
    grok.context(IPanelPage)
    grok.require('cmf.ModifyPortalContent')
    grok.name('create-asignment')

    def update(self):
        context = aq_inner(self.context)
        self.uuid = self.request.get('uuid', '')
        self.slot = self.request.get('slot', '')
        self.errors = {}
        unwanted = ('_authenticator', 'form.button.Submit', 'form.button.Clear')
        required = ('panel')
        if 'form.button.Clear' in self.request:
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
            self._clear_panel_asignment(form_data)
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
                self._update_panel_asignment(form)

    def default_value(self, error):
        value = self.uuid
        if error['active'] is False:
            value = error['msg']
        return value

    def has_asignment(self):
        value = False
        item = uuidToObject(self.uuid)
        current = getattr(item, 'panels', list())
        idx = int(self.slot) - 1
        if current >= idx:
            value = True
        return value

    def is_selected(self, value):
        selected = False
        item = uuidToObject(self.uuid)
        panels = getattr(item, 'panels', list())
        if panels and value in panels:
            selected = True
        return selected

    def available_panels(self):
        portal = api.portal.get()
        manager = portal['panel-manager']
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IContentPanel.__identifier__,
                        path=dict(query='/'.join(manager.getPhysicalPath()),
                                  depth=1),
                        sort_on='getObjPositionInParent')
        return items

    def _update_panel_asignment(self, data):
        context = aq_inner(self.context)
        item = uuidToObject(self.uuid)
        current = getattr(item, 'panels', list())
        idx = int(self.slot)
        panel = data['panel']
        if not current:
            updated = list()
            updated.append(panel)
        else:
            list_idx = len(current) - 1
            updated = current
            if panel:
                if idx > list_idx:
                    updated.append(panel)
                else:
                    del updated[idx]
                    updated.insert(idx, panel)
        setattr(item, 'panels', updated)
        modified(context)
        context.reindexObject(idxs='modified')
        base_url = context.absolute_url()
        params = '/@@panel-asignment?uuid={0}'.format(self.uuid)
        next_url = base_url + params
        return self.request.response.redirect(next_url)

    def _clear_panel_asignment(self, data):
        context = aq_inner(self.context)
        item = uuidToObject(self.uuid)
        idx = int(self.slot)
        panels = getattr(item, 'panels', list())
        del panels[idx]
        setattr(item, 'panels', panels)
        modified(context)
        context.reindexObject(idxs='modified')
        base_url = context.absolute_url()
        params = '/@@panel-asignment?uuid={0}'.format(self.uuid)
        next_url = base_url + params
        return self.request.response.redirect(next_url)


class PanelError(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('panel-error')

    def update(self):
        self.uuid = self.request.get('uuid', '')


class TransitionState(grok.View):
    grok.context(IContentish)
    grok.require('cmf.ModifyPortalContent')
    grok.name('transition-state')

    def render(self):
        context = aq_inner(self.context)
        uuid = self.request.get('uuid', '')
        state = api.content.get_state(obj=context)
        if state == 'published':
            api.content.transition(obj=context, transition='retract')
        else:
            api.content.transition(obj=context, transition='publish')
        came_from = api.content.get(UID=uuid)
        next_url = came_from.absolute_url()
        return self.request.response.redirect(next_url)
