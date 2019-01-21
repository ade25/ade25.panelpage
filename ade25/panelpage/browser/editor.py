# -*- coding: utf-8 -*-
"""Module providing panel page editor views"""
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
