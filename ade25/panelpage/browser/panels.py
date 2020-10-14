# -*- coding: utf-8 -*-
"""Module providing panel specific views"""
import json

from Acquisition import aq_inner
from ade25.widgets.interfaces import IContentWidgetTool
from plone import api
from Products.Five import BrowserView
from plone.protect.utils import addTokenToUrl
from zope.component import getUtility

from ade25.panelpage.interfaces import IPanelTool, IPanelEditor
from ade25.panelpage import MessageFactory as _


class PanelView(BrowserView):
    """ Rendered panel page """

    def __call__(self,
                 debug="off",
                 **kw):
        self.params = {
            'debug_mode': debug
        }
        self.update_panel_editor()
        return self.render()

    def render(self):
        return self.index()

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

    @staticmethod
    def panel_editor():
        tool = getUtility(IPanelEditor)
        return tool.get()

    def is_editable(self):
        context = aq_inner(self.context)
        return self.panel_tool.check_permission(context.UID())

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
        if self.panel_page_support_enabled() and self.is_editable():
            # Explicitly check for permissions
            current_user = api.user.get_current()
            display_toolbar = api.user.has_permission(
                'Ade25 Panel Page: Manage Panels',
                user=current_user,
                obj=context
            )
        return display_toolbar

    def display_page_section(self,  section):
        widgets = self.widget_tool.section_widgets(section)
        assigned_widgets = list()
        for widget_info in widgets.values():
            assigned_widgets.extend(widget_info['items'])
        if assigned_widgets:
            return True
        return False

    def stored_panels(self):
        context = aq_inner(self.context)
        panel_data = {
            "header": self.panel_tool.read(context.UID(), section='header'),
            "main": self.panel_tool.read(context.UID(), section='main'),
            "footer": self.panel_tool.read(context.UID(), section='footer')
        }
        return panel_data

    def has_panels(self):
        if self.stored_panels():
            return True
        return False

    def content_panels(self):
        return self.stored_panels()

    def panels(self):
        content_panels = [
            json.loads(panel) for panel in self.stored_panels()
        ]
        return content_panels

    @staticmethod
    def update_panel_editor():
        tool = getUtility(IPanelEditor)
        tool.reset()


class ContentPanelList(BrowserView):
    """ Embeddable panel list """
    def __call__(self,
                 identifier=None,
                 section='main',
                 mode='view',
                 **kw):
        self.params = {
            'panel_page_identifier': identifier,
            'panel_page_section': section,
            'panel_page_mode': mode
        }
        return self.render()

    def render(self):
        return self.index()

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

    def is_editable(self):
        context = aq_inner(self.context)
        return self.panel_tool.check_permission(context.UID())

    def available_widgets(self):
        widgets = self.widget_tool.section_widgets(
            self.settings["panel_page_section"]
        )
        return widgets

    def stored_panels(self):
        context = aq_inner(self.context)
        identifier = self.settings['panel_page_identifier']
        if not identifier:
            identifier = context.UID()
        panel_data = self.panel_tool.read(
            identifier,
            section=self.settings['panel_page_section']
        )
        return panel_data

    def has_content_panels(self):
        return len(self.stored_panels()) > 0

    def content_panels(self):
        content_panels = [
            json.loads(panel) for panel in self.stored_panels()
        ]
        return content_panels

    @staticmethod
    def panel_widget(panel):
        widget_data = panel['widget']
        return widget_data

    @staticmethod
    def computed_panel_class(content_panel):
        css_class = 'c-panel--{0} c-panel--{1} u-display--{2}'.format(
            content_panel.get('layout', "full-width"),
            content_panel.get("design", "default"),
            content_panel.get("display", "block")
        )
        return css_class

    @staticmethod
    def computed_panel_content_class(content_panel):
        css_class = "c-panel__main"
        layout = content_panel.get('layout', 'full-width')
        if layout.startswith('container'):
            css_class += " c-panel__main--container"
        if layout.endswith('centered'):
            css_class += " c-panel__main--centered"
        return css_class

    @staticmethod
    def panel_widget_action(url):
        return addTokenToUrl(url)


class ContentPanelOverview(BrowserView):
    """ Embeddable panel list """
    def __call__(self,
                 identifier=None,
                 section='main',
                 mode='view',
                 debug="off",
                 **kw):
        self.params = {
            'panel_page_identifier': identifier,
            'panel_page_section': section,
            'panel_page_mode': mode,
            'debug_mode': debug
        }
        return self.render()

    def render(self):
        return self.index()

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

    def is_editable(self):
        context = aq_inner(self.context)
        return self.panel_tool.check_permission(context.UID())

    def available_widgets(self):
        widgets = self.widget_tool.section_widgets(
            self.settings["panel_page_section"]
        )
        return widgets

    def stored_panels(self, page_section='main'):
        context = aq_inner(self.context)
        identifier = self.settings['panel_page_identifier']
        if not identifier:
            identifier = context.UID()
        panel_data = self.panel_tool.read(
            identifier,
            section=page_section
        )
        return panel_data

    def has_content_panels(self, page_section):
        return len(self.stored_panels(page_section)) > 0

    def content_panels(self, page_section):
        content_panels = [
            json.loads(panel) for panel in self.stored_panels(page_section)
        ]
        return content_panels

    @staticmethod
    def panel_widget(panel):
        widget_data = panel['widget']
        return widget_data

    @staticmethod
    def widget_configuration(widget_type):
        widget_tool = getUtility(IContentWidgetTool)
        widget_id = widget_type
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

    def widget_edit_action(self, section, panel):
        context = aq_inner(self.context)
        url = '{0}/@@panel-edit?section={1}&panel={2}'.format(
            context.absolute_url(),
            section,
            panel
        )
        return url

    def widget_delete_action(self, section, panel):
        context = aq_inner(self.context)
        url = '{0}/@@panel-delete?section={1}&panel={2}'.format(
            context.absolute_url(),
            section,
            panel
        )
        return url

    @staticmethod
    def computed_panel_class(content_panel):
        css_class = 'c-panel--{0} c-panel--{1} u-display--{2}'.format(
            content_panel.get('layout', "full-width"),
            content_panel.get("design", "default"),
            content_panel.get("display", "block")
        )
        return css_class

    @staticmethod
    def computed_panel_content_class(content_panel):
        css_class = "c-panel__main"
        layout = content_panel.get('layout', 'full-width')
        if layout.startswith('container'):
            css_class += " c-panel__main--container"
        if layout.endswith('centered'):
            css_class += " c-panel__main--centered"
        return css_class

    @staticmethod
    def panel_widget_action(url):
        return addTokenToUrl(url)


class PanelPageDataJSON(BrowserView):
    """ JSON representation of stored panel layout """

    def __call__(self,
                 identifier=None,
                 section='main',
                 mode='view',
                 **kw):
        self.params = {
            'panel_page_identifier': identifier,
            'panel_page_section': section,
            'panel_page_mode': mode
        }
        return self.render()

    @property
    def settings(self):
        return self.params

    @property
    def panel_tool(self):
        tool = getUtility(IPanelTool)
        return tool

    def stored_panels(self):
        context = aq_inner(self.context)
        identifier = self.settings['panel_page_identifier']
        if not identifier:
            identifier = context.UID()
        panel_data = self.panel_tool.read(
            identifier,
            section=self.settings['panel_page_section']
        )
        return panel_data

    def has_content_panels(self):
        return len(self.stored_panels()) > 0

    def content_panels(self):
        content_panels = [
            json.loads(panel) for panel in self.stored_panels()
        ]
        return content_panels

    @staticmethod
    def panel_widget(panel):
        widget_data = panel['widget']
        return widget_data

    def render(self):
        msg = _(u"Panel page data not available")
        data = {
            'success': False,
            'message': msg
        }
        layout = self.content_panels()
        if layout:
            data = layout
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return json.dumps(data)
