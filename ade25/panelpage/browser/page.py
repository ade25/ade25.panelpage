# -*- coding: utf-8 -*-
"""Module providing layout page views"""
from Acquisition import aq_inner
from Products.Five import BrowserView


class PageView(BrowserView):
    """ Standalone panel page usable as landing page """

    def panel_page(self):
        context = aq_inner(self.context)
        partial = context.restrictedTraverse('@@panelpage')()
        return partial
