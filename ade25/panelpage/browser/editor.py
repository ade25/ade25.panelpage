# -*- coding: utf-8 -*-
"""Module providing panel page editor views"""
from Acquisition import aq_inner
from Products.Five import BrowserView
from ade25.panelpage.interfaces import IPanelTool
from plone import api
from zope.component import getUtility


class PanelEditorToolbar(BrowserView):
    """ Rendered panel page toolbar"""

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

    def show_toolbar(self):
        context = aq_inner(self.context)
        display_toolbar = False
        if self.panel_page_support_enabled() and self.is_editable():
            # Explicitly check for permissions
            current_user = api.user.get_current()
            display_toolbar = api.user.has_permission(
                'ade25.panelpage.managePanels',
                current_user,
                context
            )
        return display_toolbar
