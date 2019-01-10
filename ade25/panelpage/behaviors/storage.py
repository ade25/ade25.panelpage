# -*- coding: utf-8 -*-
"""Module providing behavior to store content panel data"""
from plone import api
from plone.autoform import directives as form_directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import directives as model_directives
from plone.supermodel import model
from plone.z3cform.textlines import TextLinesFieldWidget
from zope import schema
from zope.component import adapter
from zope.interface import alsoProvides, implementer

from ade25.panelpage.interfaces import IPanelPage

from ade25.panelpage import MessageFactory as _


class IContentPanelStorage(model.Schema):
    """Behavior providing a list of panel row strings parsable as JSON"""

    model_directives.fieldset(
        'panels',
        label=u"Content Panels",
        fields=['contentPanelsHeader',
                'contentPanelsMain',
                'contentPanelsFooter'
                ]
    )

    #if not api.env.debug_mode():
    #    form_directives.omitted("contentPanelsHeader")
    #    form_directives.omitted("contentPanelsMain")
    #    form_directives.omitted("contentPanelsFooter")

    contentPanelsHeader = schema.List(
        title=_("Content Panels Header"),
        value_type=schema.TextLine(
            title=_(u"Header Panel"),
        ),
        required=False,
    )
    contentPanelsMain = schema.List(
        title=_("Content Panels Main"),
        value_type=schema.TextLine(
            title=_(u"Main Panel"),
        ),
        required=False,
    )
    contentPanelsFooter = schema.List(
        title=_("Content Panels Footer"),
        value_type=schema.TextLine(
            title=_(u"Footer Panel"),
        ),
        required=False,
    )


alsoProvides(IContentPanelStorage, IFormFieldProvider)


@implementer(IContentPanelStorage)
@adapter(IDexterityContent)
class ContentPanelStorage(object):

    def __init__(self, context):
        self.context = context
