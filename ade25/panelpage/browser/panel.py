# -*- coding: utf-8 -*-
"""Module providing panel views"""
import json
import os
import time
import datetime
import uuid as uuid_tool

from AccessControl import Unauthorized
from Acquisition import aq_inner
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from ade25.panelpage.interfaces import IPanelTool
from ade25.widgets.interfaces import IContentWidgetTool, IContentWidgets
from plone import api
from plone.app.z3cform import layout
from plone.autoform.form import AutoExtensibleForm

from plone.i18n.normalizer import IIDNormalizer
from z3c.form import button
from z3c.form import form
from plone.z3cform import layout

from zope.component import queryUtility, getUtility, getMultiAdapter

from ade25.base.utils import get_filesystem_template
from ade25.widgets import utils as widget_utils

from ade25.panelpage.interfaces import IContentPanelSettings

from ade25.panelpage import MessageFactory as _


class PanelDefaultSettings(BrowserView):
    """ Base widget used as placeholder """

    def __call__(self, widget_type="base"):
        self.widget_type = widget_type
        return self.render()

    def build_default_configuration(self):
        """ Build default panel configuration

        Addon packages are expected to add their custom widget configuration
        requirements to the registry during import and initialization and these
        will be used as panel setting keys
        """
        template = get_filesystem_template(
            'content-panel.json',
            os.path.dirname(os.path.dirname(__file__)),
            data={
                "id": str(uuid_tool.uuid4()),
                "timestamp": str(int(time.time())),
                "created": datetime.datetime.now().isoformat(),
                "widget_id": str(uuid_tool.uuid4()),
                "widget_type": self.widget_type
            }
        )
        try:
            panel_setting_template = json.loads(template)
            settings = json.dumps(panel_setting_template)
        except ValueError:
            settings = '{}'
        return safe_unicode(settings)

    def render(self):
        msg = _(u"Panel configuration data not available")
        data = {
            'success': False,
            'message': msg
        }
        settings = self.build_default_configuration()
        if settings:
            data = settings
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return data


class ContentPanel(BrowserView):
    """ Basic content panel view  """

    def __call__(self, data=None, mode="view", **kw):
        self.params = {"mode": mode, "data": data}
        return self.render()

    def render(self):
        return self.index()

    @staticmethod
    def can_edit():
        return not api.user.is_anonymous()

    @staticmethod
    def normalizer():
        return queryUtility(IIDNormalizer)

    def card_subject_classes(self, item):
        context = item
        subjects = context.Subject()
        class_list = [
            "app-card-tag--{0}".format(self.normalizer().normalize(keyword))
            for keyword in subjects
        ]
        return class_list

    def card_css_classes(self, item):
        class_list = self.card_subject_classes(item)
        if class_list:
            return " ".join(class_list)
        else:
            return "app-card-tag--all"

    @staticmethod
    def has_image(context):
        try:
            lead_img = context.image
        except AttributeError:
            lead_img = None
        if lead_img is not None:
            return True
        return False

    def widget_content(self):
        context = aq_inner(self.context)
        panel_data = self.params["data"]
        details = {

        }
        import pdb; pdb.set_trace()
        return details


class ContentPanelEdit(BrowserView):

    def __call__(self,
                 identifier=None,
                 section='main',
                 panel=None,
                 debug='off',
                 *args,
                 **kwargs):
        params = {
            'panel_page_identifier': identifier,
            'panel_page_section': self.request.get('section', section),
            'panel_page_item': self.request.get('index', panel),
            'debug_mode': debug
        }
        params.update(kwargs)
        self.params = params
        return self.render()

    def render(self):
        return self.index()

    @staticmethod
    def can_edit():
        return not api.user.is_anonymous()

    @property
    def settings(self):
        return self.params

    @property
    def panel_tool(self):
        tool = getUtility(IPanelTool)
        return tool

    def stored_panel(self):
        context = aq_inner(self.context)
        identifier = self.settings['panel_page_identifier']
        if not identifier:
            identifier = context.UID()
        panel_data = self.panel_tool.read(
            identifier,
            section=self.settings['panel_page_section'],
            key=self.settings['panel_page_item']
        )
        return panel_data

    def content_panel(self):
        content_panel = json.loads(self.stored_panel())
        return content_panel

    def content_panel_widget(self):
        return self.content_panel()['widget']

    def widget_configuration(self):
        widget_tool = getUtility(IContentWidgetTool)
        widget = self.content_panel_widget()
        widget_id = widget['type']
        try:
            configuration = widget_tool.widget_setup(
                widget_id
            )
        except KeyError:
            configuration = {
                "pkg": "PKG Undefined",
                "id": widget_id,
                "name": widget_id.replace('-', ' ').title(),
                "title": widget_id.replace('-', ' ').title(),
                "category": "more",
                "type": "base"
            }
        return configuration

    def widget_settings(self):
        widget_identifier = self.content_panel_widget()['type']
        widget_tool = getUtility(IContentWidgetTool)
        try:
            settings = widget_tool.widget_setup(widget_identifier)
        except KeyError:
            settings = {}
        return settings

    def widget_data(self):
        widget_tool = getUtility(IContentWidgetTool)
        return widget_tool.section_widgets(self.settings['panel_page_section'])

    def content_widget_data(self, widget_id):
        context = aq_inner(self.context)
        widget_data = {
            'widget_id': widget_id,
            'data': {
                'state': 'draft',
                'content': dict()
            }
        }
        storage = IContentWidgets(context)
        if storage.has_widgets():
            widget_data['data'] = storage.read_widget(widget_id)
        return widget_data


class ContentPanelCreate(BrowserView):

    def __call__(self,
                 index=0,
                 section="view",
                 **kw):
        self.params = {
            "panel_page_item": self.request.get('index', 0),
            "panel_page_section": self.request.get('section', 'main')
        }
        self.params.update(kw)
        return self.render()

    def update(self):
        self.errors = dict()
        unwanted = ('_authenticator', 'form.button.Submit')
        required = ('panel_page_widget', )
        if 'form.button.Submit' in self.request:
            authenticator = getMultiAdapter((self.context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            form = self.request.form
            form_data = {}
            form_data.update(self.params)
            form_errors = {}
            error_idx = 0
            for value in form:
                if value not in unwanted:
                    form_data[value] = safe_unicode(form[value])
                    if not form[value] and value in required:
                        form_errors[value] = self.required_field_error()
                        error_idx += 1
                    else:
                        error = {
                            'active': False,
                            'msg': form[value]
                        }
                        form_errors[value] = error
            if error_idx > 0:
                self.errors = form_errors
            else:
                self._create_panel(form)

    def render(self):
        self.update()
        return self.index()

    @staticmethod
    def can_edit():
        return not api.user.is_anonymous()

    @property
    def settings(self):
        return self.params

    @property
    def panel_tool(self):
        tool = getUtility(IPanelTool)
        return tool

    @property
    def widget_tool(self):
        tool = getUtility(IContentWidgetTool)
        return tool

    @property
    def stored_selector_sections(self):
        categories = widget_utils.content_widget_types()
        return categories

    def stored_section_widgets(self):
        data = self.widget_tool.section_widgets(
            self.settings['panel_page_section']
        )
        return data

    def selector_data(self):
        records = self.stored_section_widgets()
        for record, record_data in self.stored_section_widgets().items():
            if not record_data['items']:
                del records[record]
        return records

    def selector_sections(self):
        selector_data = self.selector_data()
        selector_list = selector_data.keys()
        original_list = self.stored_selector_sections
        return sorted(selector_list, key=lambda x: original_list.index(x))

    def selector_section_items(self, section):
        return self.selector_data()[section]

    @staticmethod
    def required_field_error():
        translation_service = api.portal.get_tool(name="translation_service")
        error = {}
        error_msg = _(u"This field is required")
        error['active'] = True
        error['msg'] = translation_service.translate(
            error_msg,
            'ade25.contacts',
            target_language=api.portal.get_default_language()
        )
        return error

    def _create_panel(self, form_data):
        context = aq_inner(self.context)
        i18n_service = api.portal.get_tool(name="translation_service")
        success_message = _(u"Content Panel created")
        message = i18n_service.translate(
            success_message,
            'ade25.panelpage',
            target_language=api.portal.get_default_language()
        )
        selected_widget_type = 'base'
        if 'panel_page_widget' in form_data:
            selected_widget_type = form_data['panel_page_widget']
        panel_data = self.panel_tool.create(
            context.UID(),
            section=form_data['panel_page_section'],
            widget_type=selected_widget_type,
            widget_position=form_data['panel_page_item']
        )
        next_url = '{0}/@@panel-edit?section={1}&index={2}'.format(
            context.absolute_url(),
            form_data['panel_page_section'],
            form_data['panel_page_item']
        )
        api.portal.show_message(message=message,
                                request=self.request,
                                type='info')
        return self.request.response.redirect(next_url)


class ContentPanelDelete(BrowserView):

    def __call__(self,
                 identifier=None,
                 section='main',
                 panel=None,
                 **kw):
        self.params = {
            'panel_page_identifier': identifier,
            'panel_page_section': self.request.get('section', section),
            'panel_page_item': self.request.get('index', panel)
        }
        self.params.update(kw)
        return self.render()

    def update(self):
        self.errors = dict()
        unwanted = ('_authenticator', 'form.button.Submit')
        required = ('panel_page_widget', )
        if 'form.button.Submit' in self.request:
            authenticator = getMultiAdapter((self.context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            form = self.request.form
            form_data = {}
            form_data.update(self.params)
            form_errors = {}
            error_idx = 0
            for value in form:
                if value not in unwanted:
                    form_data[value] = safe_unicode(form[value])
                    if not form[value] and value in required:
                        form_errors[value] = self.required_field_error()
                        error_idx += 1
                    else:
                        error = {
                            'active': False,
                            'msg': form[value]
                        }
                        form_errors[value] = error
            if error_idx > 0:
                self.errors = form_errors
            else:
                self._remove_panel(form)

    def render(self):
        self.update()
        return self.index()

    @staticmethod
    def can_edit():
        return not api.user.is_anonymous()

    @property
    def settings(self):
        return self.params

    @property
    def panel_tool(self):
        tool = getUtility(IPanelTool)
        return tool

    def stored_panel(self):
        context = aq_inner(self.context)
        identifier = self.settings['panel_page_identifier']
        # Test for existing identifier by using the string value form the
        # settings dictionary
        if identifier == 'None':
            identifier = context.UID()
        panel_data = self.panel_tool.read(
            identifier,
            section=self.settings['panel_page_section'],
            key=self.settings['panel_page_item']
        )
        return panel_data

    def content_panel(self):
        content_panel = json.loads(self.stored_panel())
        return content_panel

    def content_panel_widget(self):
        return self.content_panel()['widget']

    def widget_configuration(self):
        widget_tool = getUtility(IContentWidgetTool)
        widget = self.content_panel_widget()
        widget_id = widget['type']
        try:
            configuration = widget_tool.widget_setup(
                widget_id
            )
        except KeyError:
            configuration = {
                "pkg": "PKG Undefined",
                "id": widget_id,
                "name": widget_id.replace('-', ' ').title(),
                "title": widget_id.replace('-', ' ').title(),
                "category": "more",
                "type": "base"
            }
        return configuration

    def widget_data(self):
        widget_tool = getUtility(IContentWidgetTool)
        return widget_tool.section_widgets(self.settings['panel_page_section'])

    def content_widget_data(self, widget_id):
        context = aq_inner(self.context)
        widget_data = {
            'widget_id': widget_id,
            'data': {
                'state': 'draft',
                'content': dict()
            }
        }
        storage = IContentWidgets(context)
        if storage.has_widgets():
            widget_data['data'] = storage.read_widget(widget_id)
        return widget_data

    def _remove_panel(self, form_data):
        context = aq_inner(self.context)
        i18n_service = api.portal.get_tool(name="translation_service")
        success_message = _(u"Content Panel successfully removed")
        message = i18n_service.translate(
            success_message,
            'ade25.panelpage',
            target_language=api.portal.get_default_language()
        )
        self.panel_tool.delete(
            context.UID(),
            section=form_data['panel_page_section'],
            widget_position=form_data['panel_page_item']
        )
        next_url = '{0}/@@panel-page'.format(
            context.absolute_url()
        )
        api.portal.show_message(message=message,
                                request=self.request,
                                type='info')
        return self.request.response.redirect(next_url)


class ContentPanelSettingsForm(AutoExtensibleForm, form.Form):

    schema = IContentPanelSettings
    ignoreContext = False
    css_class = 'o-form o-form--panels o-form--panel-settings'
    label = _(u"Update content panel settings")

    def next_url(self):
        context = aq_inner(self.context)
        url = '{0}/@@panel-page'.format(
            context.absolute_url()
        )
        return url

    def getContent(self):
        item = aq_inner(self.context)
        # TODO: Read data form panel settings
        data = {
            'custom_class': getattr(self.request, 'widget_class', 'c-widget'),
            'section': getattr(self.request, 'section', ''),
            'panel': getattr(self.request, 'panel', ''),
            'identifier': getattr(self.request, 'identifier', ''),
        }
        return data

    def applyChanges(self, data):
        pass

    @button.buttonAndHandler(u"Delete Panel", name='delete')
    def handleDelete(self, action):
        """Delete panel and all stored contents. Redirects to conformation page.
        """
        context = aq_inner(self.context)
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        next_url = '{0}/@@panel-delete?section={1}&panel={2}&identifier={3}'.format(
            context.absolute_url(),
            data['section'],
            data['panel'],
            data['identifier']
        )
        return self.request.response.redirect(next_url)

    @button.buttonAndHandler(u'Update')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        self.status = _(u"Item added successfully.")
        IStatusMessage(self.request).addStatusMessage(
            _(u"The panel has successfully been updated"),
            type='info')
        return self.request.response.redirect(self.next_url())

    def updateActions(self):
        super(ContentPanelSettingsForm, self).updateActions()
        self.actions["update"].addClass("c-button--primary")
        self.actions["delete"].addClass("c-button--danger")

    def updateWidgets(self):
        super(ContentPanelSettingsForm, self).updateWidgets()


ContentPanelSettingsFormView = layout.wrap_form(ContentPanelSettingsForm)
