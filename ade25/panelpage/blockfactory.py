from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from plone import api
from zope import schema
from zope.schema import getFieldsInOrder
from zope.component import getUtility

from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button

from Products.CMFPlone.utils import safe_unicode
from plone.namedfile.field import NamedBlobImage
from plone.app.textfield import RichText

from plone.dexterity.interfaces import IDexterityFTI
from Products.statusmessages.interfaces import IStatusMessage

from ade25.panelpage.contentblock import IContentBlock

from ade25.panelpage import MessageFactory as _


class IContentBlockEdit(form.Schema):

    headline = schema.TextLine(
        title=_(u"Content Block Headline"),
        description=_(u"Optional headline for this block"),
        required=False,
    )
    description = schema.Text(
        title=_(u"Teaser"),
        description=_(u"Short and visualy highlighted teaser message"),
        required=False,
    )
    text = RichText(
        title=_(u"Block Body Text"),
        required=False,
    )


class IContentBlockImageEdit(form.Schema):

    image = NamedBlobImage(
        title=_(u"Image"),
        required=False,
    )
    imageRight = schema.Bool(
        title=_(u"Right align image"),
        description=_(u"Change the default image position to the right third"),
        required=False,
    )


class ContentBlockEditForm(form.SchemaEditForm):
    grok.context(IContentBlock)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-block')

    schema = IContentBlockEdit
    ignoreContext = False
    css_class = 'app-form'

    label = _(u"Edit content panel")

    def updateActions(self):
        super(ContentBlockEditForm, self).updateActions()
        self.actions['save'].addClass("btn btn-primary btn-editpanel")
        self.actions['cancel'].addClass("btn btn-default")

    @button.buttonAndHandler(_(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content block factory has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.contentblock')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.contentblock')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        for key, value in fields:
            try:
                new_value = data[key]
                setattr(context, key, new_value)
            except KeyError:
                continue
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The content block has successfully been updated"),
            type='info')
        parent = aq_parent(context)
        next_url = parent.absolute_url() + '/@@panelpage-editor'
        return self.request.response.redirect(next_url)


class ContentBlockImageEditForm(form.SchemaEditForm):
    grok.context(IContentBlock)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-block-image')

    schema = IContentBlockImageEdit
    ignoreContext = False
    css_class = 'app-form'

    label = _(u"Edit content block image content")

    def updateActions(self):
        super(ContentBlockImageEditForm, self).updateActions()
        self.actions['save'].addClass("btn btn-primary btn-editpanel")
        self.actions['cancel'].addClass("btn btn-default")

    @button.buttonAndHandler(_(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content block factory has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.contentblock')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.contentblock')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        for key, value in fields:
            try:
                new_value = data[key]
                setattr(context, key, new_value)
            except KeyError:
                continue
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"This block has successfully been updated"),
            type='info')
        parent = aq_parent(context)
        next_url = parent.absolute_url() + '/@@panelpage-editor'
        return self.request.response.redirect(next_url)
