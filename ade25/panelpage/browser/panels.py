# -*- coding: utf-8 -*-
"""Module providing panel specific views"""
import json

from Acquisition import aq_inner
from plone import api
from Products.Five import BrowserView
from zope.component import getUtility

from ade25.panelpage.interfaces import IPanelTool, IPanelEditor
from ade25.panelpage import MessageFactory as _


class PanelView(BrowserView):
    """ Rendered panel page """

    def __call__(self):
        self.update_panel_editor()
        return self.render()

    def render(self):
        return self.index()

    @property
    def panel_tool(self):
        tool = getUtility(IPanelTool)
        return tool

    @staticmethod
    def is_editable():
        editable = False
        if not api.user.is_anonymous():
            editable = True
        return editable

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
        return tool.get()


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
            content_panel['layout'],
            content_panel['design'],
            content_panel['display']
        )
        return css_class


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
