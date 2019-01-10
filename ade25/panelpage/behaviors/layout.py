# -*- coding: utf-8 -*-
"""Module providing JSON storage for panel page contents"""
import json

from Acquisition import aq_inner
from plone import api
from plone.autoform import directives as form_directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import directives as model_directives
from plone.supermodel import model
from plone.z3cform.textlines import TextLinesFieldWidget
from zope import schema
from zope.component import adapter, getUtility
from zope.interface import implementer
from zope.interface import provider

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

    model_directives.fieldset(
        'panels',
        label=u"Panels",
        fields=['panelLayout',
                ]
    )

    if not api.env.debug_mode():
        #form_directives.omitted("panelPageLayout")
        form_directives.omitted("panelLayout")

    # directives.omitted('panelLayout')
    panelLayout = schema.TextLine(
        title=_("Panel Layout"),
        required=False,
        # defaultFactory=panel_layout_default_value,
    )


@implementer(IPanelPageLayout)
@adapter(IDexterityContent)
class PanelPageLayout(object):

    def __init__(self, context):
        self.context = context
