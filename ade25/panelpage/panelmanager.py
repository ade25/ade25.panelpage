from Acquisition import aq_inner
from AccessControl import Unauthorized
from five import grok
from plone import api

from zope.component import getMultiAdapter

from plone.keyring import django_random
from plone.directives import form
from plone.dexterity.content import Container
from Products.CMFPlone.utils import safe_unicode

from ade25.panelpage.contentpanel import IContentPanel

from ade25.panelpage import MessageFactory as _


class IPanelManager(form.Schema):
    """
    Folder ccontaining content panels and showing overviews
    """


class PanelManager(Container):
    grok.implements(IPanelManager)
    pass


class View(grok.View):
    grok.context(IPanelManager)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        self.has_panels = len(self.contentpanels()) > 0
        self.errors = {}
        unwanted = ('_authenticator', 'form.button.Submit')
        required = ('title')
        if 'form.button.Submit' in self.request:
            authenticator = getMultiAdapter((self.context, self.request),
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
        return not api.user.is_anonymous()

    def get_rendered_block(self, uid):
        item = api.content.get(UID=uid)
        template = item.restrictedTraverse('@@content-view')()
        return template

    def contentpanels(self):
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IContentPanel.__identifier__,
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
            type='ade25.panelpage.contentpanel',
            id=token,
            title=new_title,
            container=context,
            safe_id=True
        )
        url = context.absolute_url()
        return self.request.response.redirect(url)


class CreatePanel(grok.View):
    grok.context(IPanelManager)
    grok.require('cmf.ModifyPortalContent')
    grok.name('create-panel')

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
        api.content.create(
            type='ade25.panelpage.contentpanel',
            id=token,
            title=new_title,
            container=context,
            safe_id=True
        )
        url = context.absolute_url()
        next_url = url + '&token=' + token
        return self.request.response.redirect(next_url)
