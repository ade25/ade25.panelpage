# -*- coding: utf-8 -*-
"""Module providing panel specific views"""
import json

from Acquisition import aq_inner
from plone import api
from Products.Five import BrowserView

from ade25.panelpage import MessageFactory as _


class PanelView(BrowserView):
    """ Rendered panel page """

    def __call__(self):
        return self.render()

    def render(self):
        return self.index()

    def is_editable(self):
        editable = False
        if not api.user.is_anonymous():
            editable = True
        return editable

    def rendered_panel_grid(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@panelgrid')()
        return template

    def computed_styles(self):
        klass = 'panel-page--default'
        if self.is_editable():
            klass = 'panel-page--editable'
        return klass

    def has_stored_layout(self):
        context = aq_inner(self.context)
        if hasattr(context.aq_explicit, 'panelPageLayout'):
            stored = getattr(context, 'panelPageLayout')
            if stored is not None:
                return True
        return False


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
        layout = getattr(context, 'panelPageLayout', None)
        if layout:
            data = layout
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return json.dumps(data)
