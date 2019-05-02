# -*- coding: utf-8 -*-
"""Module providing standalone content panel edit forms"""
from Acquisition import aq_inner
from Products.statusmessages.interfaces import IStatusMessage
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from zope import schema
from plone.autoform.form import AutoExtensibleForm
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from plone.z3cform import layout
from ade25.panelpage import MessageFactory as _
from zope.component import getUtility
from zope.interface import Interface, provider
from zope.lifecycleevent import modified
from zope.schema import getFieldsInOrder
from z3c.form import button
from z3c.form import form


@provider(IFormFieldProvider)
class IContentPanelEditForm(Interface):
    """ Content Panel Storage Slots """

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


class ContentPanelsEditForm(AutoExtensibleForm, form.Form):

    schema = IContentPanelEditForm
    ignoreContext = False
    css_class = 'o-form o-form--panels'
    label = _(u"Edit content panel json storage")

    def next_url(self):
        context = aq_inner(self.context)
        url = '{0}/@@panel-page-view'.format(
            context.absolute_url()
        )
        return url

    def getContent(self):
        item = aq_inner(self.context)
        data = {
            'contentPanelsHeader': getattr(item, 'contentPanelsHeader'),
            'contentPanelsMain': getattr(item, 'contentPanelsMain'),
            'contentPanelsFooter': getattr(item, 'contentPanelsFooter')
        }
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        setattr(context, 'contentPanelsHeader', data['contentPanelsHeader'])
        setattr(context, 'contentPanelsMain', data['contentPanelsMain'])
        setattr(context, 'contentPanelsFooter', data['contentPanelsFooter'])
        modified(context)
        context.reindexObject(idxs='modified')

    @button.buttonAndHandler(u'Update')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        self.status = _(u"Item added successfully.")
        IStatusMessage(self.request).addStatusMessage(
            _(u"The panel has successfully been updated"),
            type='info')
        return self.request.response.redirect(self.next_url())

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        context = aq_inner(self.context)
        next_url = context.absolute_url()
        return self.request.response.redirect(next_url)

    def updateActions(self):
        super(ContentPanelsEditForm, self).updateActions()
        self.actions["update"].addClass("c-button--primary")

    def updateWidgets(self):
        super(ContentPanelsEditForm, self).updateWidgets()


ContentPanelsEditFormView = layout.wrap_form(ContentPanelsEditForm)
