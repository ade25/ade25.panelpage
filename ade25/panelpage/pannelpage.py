# -*- coding: utf-8 -*-
"""Module providing ContentPage content type functionality"""

from plone.dexterity.content import Item
from plone.supermodel import model
from plone.namedfile.interfaces import IImageScaleTraversable
from zope.interface import implementer


class IPanelPage(model.Schema, IImageScaleTraversable):
    """
    A container with enabled layout support that can be used as landing page
    """


@implementer(IPanelPage)
class PanelPage(Item):
    pass
