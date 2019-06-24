# -*- coding: utf-8 -*-
"""Module providing panel page editor views"""
from Acquisition import aq_inner
from Products.Five import BrowserView
from ade25.panelpage.interfaces import IPanelTool, IPanelEditor
from plone import api
from zope.component import getUtility


class PanelEditorToolbar(BrowserView):
    """ Rendered panel page toolbar"""

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
                'Ade25 Panel Page: Manage Panels',
                user=current_user,
                obj=context
            )
        return display_toolbar


class PanelEditorReset(BrowserView):
    """ Reset panel editor session storage """

    def __call__(self):
        return self.render()

    def render(self):
        context = aq_inner(self.context)
        tool = getUtility(IPanelEditor)
        tool.destroy()
        next_url = context.absolute_url()
        return self.request.response.redirect(next_url)

