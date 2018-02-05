# -*- coding: utf-8 -*-
"""Module providing JSON storage for panel page contents"""
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider
from zope import schema

from ade25.panelpage import MessageFactory as _


@provider(IFormFieldProvider)
class IPanelPageLayout(model.Schema):
    """Behavior providing a list of panel row strings parsable as JSON"""

    directives.omitted('panelPageLayout')
    panelPageLayout = schema.List(
        title=_("Panel Page Layout"),
        value_type=schema.TextLine(
            title=_(u"Content Page Layout"),
        ),
        required=False,
    )


@implementer(IPanelPageLayout)
@adapter(IDexterityContent)
class PanelPageLayout(object):

    def __init__(self, context):
        self.context = context
