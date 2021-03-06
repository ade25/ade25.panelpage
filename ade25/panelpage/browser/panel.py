# -*- coding: utf-8 -*-
"""Module providing panel views"""
import json
import os
import pickle
import time
import datetime
import uuid as uuid_tool

from AccessControl import Unauthorized
from Acquisition import aq_inner
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from ade25.panelpage.interfaces import IPanelTool, IPanelEditor
from ade25.widgets.interfaces import IContentWidgetTool, IContentWidgets
from plone import api
from plone.app.z3cform import layout
from plone.autoform.form import AutoExtensibleForm

from plone.i18n.normalizer import IIDNormalizer
from plone.protect.utils import addTokenToUrl
from plone.z3cform.layout import FormWrapper
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
        return details


class ContentPanelEdit(BrowserView):

    def __call__(self,
                 identifier=None,
                 section='main',
                 panel=None,
                 debug='off',
                 cleanup='off',
                 *args,
                 **kwargs):
        params = {
            'panel_page_identifier': identifier,
            'panel_page_section': self.request.get('section', section),
            'panel_page_item': self.request.get('index', panel),
            'debug_mode': debug,
            'cleanup_mode': cleanup
        }
        params.update(kwargs)
        self.params = params
        self._update_panel_editor(self.params)
        return self.render()

    def render(self):
        return self.index()

    @staticmethod
    def can_edit():
        return not api.user.is_anonymous()

    @property
    def settings(self):
        return self.params

    @staticmethod
    def panel_editor():
        tool = getUtility(IPanelEditor)
        return tool.get()

    @property
    def panel_tool(self):
        tool = getUtility(IPanelTool)
        return tool

    @property
    def widget_tool(self):
        widget_tool = getUtility(IContentWidgetTool)
        return widget_tool

    def stored_panel(self):
        context = aq_inner(self.context)
        identifier = self.settings['panel_page_identifier']
        if not identifier:
            identifier = context.UID()
        try:
            panel_data = self.panel_editor()[context.UID()]["panel"]
        except:
            panel_data = self.panel_tool.read(
                identifier,
                section=self.settings['panel_page_section'],
                key=self.settings['panel_page_item']
            )
        return panel_data

    def content_panel(self):
        try:
            content_panel = json.loads(self.stored_panel())
        except TypeError:
            content_panel = self.stored_panel()
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
        try:
            settings = self.widget_tool.widget_setup(widget_identifier)
        except KeyError:
            settings = {}
        return settings

    def widget_data(self):
        return self.widget_tool.section_widgets(
            self.settings['panel_page_section'])

    def content_widget_data(self, widget_id):
        context = aq_inner(self.context)
        widget_data = {}
        storage = IContentWidgets(context)
        if storage.has_widgets():
            widget_data = storage.read_widget(widget_id)
        return widget_data

    @staticmethod
    def widget_actions(content_type="default"):
        actions = [
            "create",
            "update",
            "delete",
            "settings",
        ]
        if content_type == "collection-item":
            actions = [
                "update",
                "delete",
                "reorder"
            ]
        return actions

    def widget_action(self, action_name, widget_type="base"):
        context = aq_inner(self.context)
        widget_tool = getUtility(IContentWidgetTool)
        is_current = False
        if action_name == "update":
            is_current = True
        action_details = widget_tool.widget_action_details(
            context,
            action_name,
            widget_type,
            is_current
        )
        return action_details

    @staticmethod
    def widget_action_url(action_url):
        return addTokenToUrl(action_url)

    @staticmethod
    def _validate_widget_content(content_data):
        try:
            data_hash = pickle.dumps(content_data)
            if data_hash:
                return content_data
        except (pickle.PicklingError, TypeError):
            # Return sensible error message and abort
            pass

    def _update_panel_editor(self, settings):
        context = aq_inner(self.context)
        context_uid = context.UID()
        tool = getUtility(IPanelEditor)
        if settings["cleanup_mode"]:
            tool.remove(context_uid)
        stored_widget_content = self.content_widget_data(
            self.content_panel_widget()['id']
        )
        widget_content = self._validate_widget_content(stored_widget_content)
        return tool.add(
            key=context_uid,
            data={
                'content_section': settings['panel_page_section'],
                'content_section_panel': settings['panel_page_item'],
                'panel': self.content_panel(),
                'widget_id': self.content_panel_widget()['id'],
                'widget_content': widget_content,
                'widget_settings': self.widget_settings()
            }
        )

    def panel_page_support_enabled(self):
        context = aq_inner(self.context)
        try:
            from ade25.panelpage.behaviors.storage import IContentPanelStorage
            if IContentPanelStorage.providedBy(context):
                return True
            else:
                return False
        except ImportError:
            return False

    def is_panel_page_manager(self):
        context = aq_inner(self.context)
        display_toolbar = False
        if self.panel_page_support_enabled() and self.can_edit():
            # Explicitly check for permissions
            current_user = api.user.get_current()
            display_toolbar = api.user.has_permission(
                'Ade25 Panel Page: Manage Panels',
                user=current_user,
                obj=context
            )
        return display_toolbar


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

    @staticmethod
    def panel_editor():
        tool = getUtility(IPanelEditor)
        return tool.get()

    @property
    def configuration(self):
        context = aq_inner(self.context)
        try:
            config = self.panel_editor()[context.UID()]
        except KeyError:
            config = {
                "content_section": self.settings.get("panel_page_section"),
                "content_section_panel": str(
                    self.settings.get("panel_page_item")
                )
            }
        return config

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

    @staticmethod
    def panel_editor():
        tool = getUtility(IPanelEditor)
        return tool.get()

    @property
    def configuration(self):
        context = aq_inner(self.context)
        return self.panel_editor()[context.UID()]

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

    @staticmethod
    def widget_actions(content_type="default"):
        actions = [
            "create",
            "update",
            "delete",
            "settings",
        ]
        if content_type == "collection-item":
            actions = [
                "update",
                "delete",
                "reorder"
            ]
        return actions

    def widget_action(self, action_name, widget_type="base"):
        context = aq_inner(self.context)
        widget_tool = getUtility(IContentWidgetTool)
        is_current = False
        if action_name == "delete":
            is_current = True
        action_details = widget_tool.widget_action_details(
            context,
            action_name,
            widget_type,
            is_current
        )
        return action_details

    @staticmethod
    def widget_action_url(action_url):
        return addTokenToUrl(action_url)

    def _remove_panel(self, form_data):
        context = aq_inner(self.context)
        panel_data = self.configuration
        i18n_service = api.portal.get_tool(name="translation_service")
        success_message = _(u"Content Panel successfully removed")
        message = i18n_service.translate(
            success_message,
            'ade25.panelpage',
            target_language=api.portal.get_default_language()
        )
        self.panel_tool.delete(
            context.UID(),
            section=panel_data['content_section'],
            key=panel_data['content_section_panel']
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

    enableCSRFProtection = True
    formErrorsMessage = _(u'There were errors.')

    submitted = False

    @property
    def panel_editor(self):
        tool = getUtility(IPanelEditor)
        return tool.get()

    @property
    def panel_configuration(self):
        context = aq_inner(self.context)
        return self.panel_editor[context.UID()]

    @property
    def panel_tool(self):
        tool = getUtility(IPanelTool)
        return tool

    def next_url(self):
        context = aq_inner(self.context)
        editor_data = self.panel_configuration
        url = '{0}/@@panel-edit?section={1}&panel={2}'.format(
            context.absolute_url(),
            editor_data["content_section"],
            editor_data["content_section_panel"]
        )
        return url

    def stored_panel(self):
        context = aq_inner(self.context)
        identifier = getattr(self.request, 'identifier', '')
        if not identifier:
            identifier = context.UID()
        panel_data = self.panel_tool.read(
            identifier,
            section=getattr(self.request, 'section', ''),
            key=getattr(self.request, 'panel', '')
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

    def getContent(self):
        editor_data = self.panel_configuration
        panel_settings = {
            "section": editor_data["content_section"],
            "panel": editor_data["content_section_panel"],
            "custom_class": editor_data["panel"]["widget"]["css_classes"],
            "widget_layout": editor_data["panel"]["layout"],
            "widget_display": editor_data["panel"]["display"],
            "widget_design": editor_data["panel"]["design"]
        }
        return panel_settings

    def applyChanges(self, data):
        context = aq_inner(self.context)
        editor_data = self.panel_configuration
        panel_data = self.panel_tool.read(
            context.UID(),
            section=editor_data["content_section"],
            key=editor_data["content_section_panel"]
        )
        record = json.loads(panel_data)
        record["widget"]["css_classes"] = data["custom_class"]
        record["layout"] = data["widget_layout"]
        record["display"] = data["widget_display"]
        record["design"] = data["widget_design"]
        self.panel_tool.update(
            context.UID(),
            json.dumps(record),
            section=editor_data["content_section"],
            key=editor_data["content_section_panel"]
        )

    @button.buttonAndHandler(u"Cancel", name='cancel')
    def handleCancel(self, action):
        """Delete panel and all stored contents. Redirects to conformation page.
        """
        context = aq_inner(self.context)
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        next_url = '{0}/@@panel-edit?section={1}&panel={2}'.format(
            context.absolute_url(),
            data['section'],
            data['panel']
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
        self.actions["cancel"].addClass("c-button--default")


class ContentPanelSettingsFormView(FormWrapper):

    form = ContentPanelSettingsForm

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
        self.update()
        return self.render()

    @property
    def settings(self):
        return self.params

    @staticmethod
    def panel_editor():
        tool = getUtility(IPanelEditor)
        return tool.get()

    @property
    def configuration(self):
        context = aq_inner(self.context)
        return self.panel_editor()[context.UID()]

    @staticmethod
    def widget_actions(content_type="default"):
        actions = [
            "create",
            "update",
            "delete",
            "settings",
        ]
        if content_type == "collection-item":
            actions = [
                "update",
                "delete",
                "reorder"
            ]
        return actions

    def widget_action(self, action_name, widget_type="base"):
        context = aq_inner(self.context)
        widget_tool = getUtility(IContentWidgetTool)
        is_current = False
        if action_name == "settings":
            is_current = True
        action_details = widget_tool.widget_action_details(
            context,
            action_name,
            widget_type,
            is_current
        )
        return action_details

    @staticmethod
    def widget_action_url(action_url):
        return addTokenToUrl(action_url)
