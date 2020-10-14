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

    def show_toolbar(self):
        context = aq_inner(self.context)
        return self.panel_tool.check_permission(context.UID())


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

