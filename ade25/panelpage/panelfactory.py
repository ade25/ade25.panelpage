from Acquisition import aq_inner
from five import grok
from plone import api
from zope import schema
from zope.schema import getFieldsInOrder
from zope.component import getUtility

from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button

from plone.dexterity.interfaces import IDexterityFTI
from Products.statusmessages.interfaces import IStatusMessage

from ade25.panelpage.panelpage import IPanelPage
from ade25.panelpage.interfaces import IPanelHeading
from ade25.panelpage.interfaces import IPanelSubHeading
from ade25.panelpage.interfaces import IPanelAbstract
from ade25.panelpage.interfaces import IPanelText
from ade25.panelpage.interfaces import IPanelRichText
from ade25.panelpage.interfaces import IPanelImage

from ade25.panelpage import MessageFactory as _


class PanelHeadingEditForm(form.SchemaEditForm):
    grok.context(IPanelPage)
    grok.require('cmf.AddPortalContent')
    grok.name('panel-heading')

    schema = IPanelHeading
    ignoreContext = False
    css_class = 'app-form'
    label = _(u"Edit content panel")

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    @button.buttonAndHandler(_(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        uid = self.traverse_subpath[2]
        item = api.content.get(UID=uid)
        setattr(item, 'textline', data['textline'])
        modified(item)
        item.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The panel has successfully been updated"),
            type='info')
        row = self.traverse_subpath[0]
        context = aq_inner(self.context)
        url = '{0}/@@panelblock-editor/{1}'.format(
            context.absolute_url(), row)
        return self.request.response.redirect(url)

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        row = self.traverse_subpath[0]
        url = '{0}/@@panelblock-editor/{1}'.format(context.absolute_url(), row)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content panel factory has been cancelled."),
            type='info')
        return self.request.response.redirect(url)

    def getContent(self):
        uid = self.traverse_subpath[2]
        item = api.content.get(UID=uid)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.panel')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(item, key, value)
        data['textline'] = getattr(item, 'textline', '')
        return data


class PanelSubHeadingEditForm(form.SchemaEditForm):
    grok.context(IPanelPage)
    grok.require('cmf.AddPortalContent')
    grok.name('panel-subheading')

    schema = IPanelSubHeading
    ignoreContext = False
    css_class = 'app-form'
    label = _(u"Edit content panel")

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    @button.buttonAndHandler(_(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        uid = self.traverse_subpath[2]
        item = api.content.get(UID=uid)
        setattr(item, 'textline', data['textline'])
        modified(item)
        item.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The panel has successfully been updated"),
            type='info')
        row = self.traverse_subpath[0]
        context = aq_inner(self.context)
        url = '{0}/@@panelblock-editor/{1}'.format(
            context.absolute_url(), row)
        return self.request.response.redirect(url)

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        row = self.traverse_subpath[0]
        url = '{0}/@@panelblock-editor/{1}'.format(context.absolute_url(), row)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content panel factory has been cancelled."),
            type='info')
        return self.request.response.redirect(url)

    def getContent(self):
        uid = self.traverse_subpath[2]
        item = api.content.get(UID=uid)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.panel')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(item, key, value)
        data['textline'] = getattr(item, 'textline', '')
        return data


class PanelAbstractEditForm(form.SchemaEditForm):
    grok.context(IPanelPage)
    grok.require('cmf.AddPortalContent')
    grok.name('panel-abstract')

    schema = IPanelAbstract
    ignoreContext = False
    css_class = 'app-form'
    label = _(u"Edit content panel")

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    @button.buttonAndHandler(_(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        uid = self.traverse_subpath[2]
        item = api.content.get(UID=uid)
        setattr(item, 'textblock', data['textblock'])
        modified(item)
        item.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The panel has successfully been updated"),
            type='info')
        row = self.traverse_subpath[0]
        context = aq_inner(self.context)
        url = '{0}/@@panelblock-editor/{1}'.format(
            context.absolute_url(), row)
        return self.request.response.redirect(url)

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        row = self.traverse_subpath[0]
        url = '{0}/@@panelblock-editor/{1}'.format(context.absolute_url(), row)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content panel factory has been cancelled."),
            type='info')
        return self.request.response.redirect(url)

    def getContent(self):
        uid = self.traverse_subpath[2]
        item = api.content.get(UID=uid)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.panel')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(item, key, value)
        data['textblock'] = getattr(item, 'textline', '')
        return data


class PanelTextEditForm(form.SchemaEditForm):
    grok.context(IPanelPage)
    grok.require('cmf.AddPortalContent')
    grok.name('panel-text')

    schema = IPanelText
    ignoreContext = False
    css_class = 'app-form'
    label = _(u"Edit content panel")

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    @button.buttonAndHandler(_(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        uid = self.traverse_subpath[2]
        item = api.content.get(UID=uid)
        setattr(item, 'textblock', data['textblock'])
        modified(item)
        item.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The panel has successfully been updated"),
            type='info')
        row = self.traverse_subpath[0]
        context = aq_inner(self.context)
        url = '{0}/@@panelblock-editor/{1}'.format(
            context.absolute_url(), row)
        return self.request.response.redirect(url)

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        row = self.traverse_subpath[0]
        url = '{0}/@@panelblock-editor/{1}'.format(context.absolute_url(), row)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content panel factory has been cancelled."),
            type='info')
        return self.request.response.redirect(url)

    def getContent(self):
        uid = self.traverse_subpath[2]
        item = api.content.get(UID=uid)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.panel')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(item, key, value)
        data['textblock'] = getattr(item, 'textline', '')
        return data


class PanelRichTextEditForm(form.SchemaEditForm):
    grok.context(IPanelPage)
    grok.require('cmf.AddPortalContent')
    grok.name('panel-richtext')

    schema = IPanelRichText
    ignoreContext = False
    css_class = 'app-form'
    label = _(u"Edit content panel")

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    def next_url(self):
        context = aq_inner(self.context)
        row = self.traverse_subpath[0]
        url = '{0}/@@panelblock-editor/{1}'.format(
            context.absolute_url(), row)
        return url

    def panel(self):
        uid = self.traverse_subpath[2]
        item = api.content.get(UID=uid)
        return item

    @button.buttonAndHandler(_(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        item = self.panel()
        setattr(item, 'text', data['text'])
        modified(item)
        item.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The panel has successfully been updated"),
            type='info')
        return self.request.response.redirect(self.next_url())

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content panel factory has been cancelled."),
            type='info')
        return self.request.response.redirect(self.next_url())

    def getContent(self):
        uid = self.traverse_subpath[2]
        item = api.content.get(UID=uid)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.panel')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(item, key, value)
        data['text'] = getattr(item, 'text', None)
        return data


class PanelImageEditForm(form.SchemaEditForm):
    grok.context(IPanelPage)
    grok.require('cmf.AddPortalContent')
    grok.name('panel-image')

    schema = IPanelImage
    ignoreContext = False
    css_class = 'app-form'
    label = _(u"Edit content panel")

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    def next_url(self):
        context = aq_inner(self.context)
        row = self.traverse_subpath[0]
        url = '{0}/@@panelblock-editor/{1}'.format(
            context.absolute_url(), row)
        return url

    @button.buttonAndHandler(_(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        uid = self.traverse_subpath[2]
        item = api.content.get(UID=uid)
        setattr(item, 'image', data['image'])
        modified(item)
        item.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The panel has successfully been updated"),
            type='info')
        return self.request.response.redirect(self.next_url())

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        row = self.traverse_subpath[0]
        url = '{0}/@@panelblock-editor/{1}'.format(context.absolute_url(), row)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content panel factory has been cancelled."),
            type='info')
        return self.request.response.redirect(url)

    def getContent(self):
        uid = self.traverse_subpath[2]
        item = api.content.get(UID=uid)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.panel')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(item, key, value)
        data['image'] = getattr(item, 'image')
        return data


class IPanelBaseEdit(form.Schema):

    title = schema.TextLine(
        title=_(u"Content Panel Title"),
        required=True,
    )
    klass = schema.TextLine(
        title=_(u"CSS Class"),
        required=False,
    )


class PanelBaseEditForm(form.SchemaEditForm):
    grok.context(IPanelPage)
    grok.require('cmf.AddPortalContent')
    grok.name('panel-base-edit')

    schema = IPanelImage
    ignoreContext = False
    css_class = 'app-form'
    label = _(u"Edit content panel")

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    @button.buttonAndHandler(_(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        uid = self.traverse_subpath[2]
        item = api.content.get(UID=uid)
        setattr(item, 'image', data['image'])
        modified(item)
        item.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The panel has successfully been updated"),
            type='info')
        row = self.traverse_subpath[0]
        context = aq_inner(self.context)
        url = '{0}/@@panelblock-editor/{1}'.format(
            context.absolute_url(), row)
        return self.request.response.redirect(url)

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        row = self.traverse_subpath[0]
        url = '{0}/@@panelblock-editor/{1}'.format(context.absolute_url(), row)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content panel factory has been cancelled."),
            type='info')
        return self.request.response.redirect(url)

    def getContent(self):
        uid = self.traverse_subpath[2]
        item = api.content.get(UID=uid)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.panel')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(item, key, value)
        return data


class PanelFactory(grok.View):
    grok.context(IPanelPage)
    grok.require('zope2.View')
    grok.name('panelfactory')

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    def panel(self):
        uuid = self.traverse_subpath[0]
        item = api.content.get(UID=uuid)
        return item
