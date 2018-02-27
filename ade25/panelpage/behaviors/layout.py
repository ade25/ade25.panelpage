# -*- coding: utf-8 -*-
"""Module providing JSON storage for panel page contents"""
import json

from Acquisition import aq_inner
from plone import api
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope.component import adapter, getUtility
from zope.interface import implementer
from zope.interface import provider
from zope import schema

from ade25.panelpage.interfaces import IPanelTool

from ade25.panelpage import MessageFactory as _


def panel_layout_default_value():
    tool = getUtility(IPanelTool)
    new_records = tool.create_record()
    data = json.dumps(new_records)
    return unicode(data)


@provider(IFormFieldProvider)
class IPanelPageLayout(model.Schema):
    """Behavior providing a list of panel row strings parsable as JSON"""

    # directives.omitted('panelPageLayout')
    panelPageLayout = schema.List(
        title=_("Panel Page Layout"),
        value_type=schema.TextLine(
            title=_(u"Content Page Layout"),
        ),
        required=False,
    )

    # directives.omitted('panelLayout')
    panelLayout = schema.TextLine(
        title=_("Panel Layout"),
        required=False,
        defaultFactory=panel_layout_default_value,
    )

    # directives.omitted('panelPageData')
    panelPageData = schema.List(
        title=_("Stored Panels"),
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
