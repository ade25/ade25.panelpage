# -*- coding: utf-8 -*-
"""Module providing panel specific views"""
import json

from Acquisition import aq_inner
from plone import api
from Products.Five import BrowserView
from zope.component import getUtility

from ade25.panelpage.interfaces import IPanelTool
from ade25.panelpage import MessageFactory as _


class PanelView(BrowserView):
    """ Rendered panel page """

    def __call__(self):
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


class ContentPanelList(BrowserView):
    """ Embeddable panel list """
    def __call__(self,
                 identifier=None,
                 section='main',
                 mode='view'
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
        css_class = 'c-panel c-panel--'.format(
            content_panel['id']
        )
        return css_class


class PanelPageDataJSON(BrowserView):
    """ JSON representation of stored panel layout """

    def __call__(self):
        return self.render()

    def render(self):
        context = aq_inner(self.context)
        msg = _(u"Panel page data not available")
        data = {
            'success': False,
            'message': msg
        }
        layout = getattr(context, 'panelLayout', None)
        if layout:
            data = layout
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return json.dumps(data)
