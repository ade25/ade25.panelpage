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

from plone.namedfile.field import NamedBlobImage
from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from plone.app.uuid.utils import uuidToObject

from plone.dexterity.interfaces import IDexterityFTI
from Products.statusmessages.interfaces import IStatusMessage
from ade25.panelpage.panelpage import IPanelPage
from ade25.panelpage.panelmanager import IPanelManager
from ade25.panelpage.contentpanel import IContentPanel

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
    ignoreContext = True
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
        parent = aq_parent(context)
        row = self.traverse_subpath[0]
        url = '{0}/@@panelblock-editor/{1}'.format(parent.absolute_url(), row)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content panel factory has been cancelled."),
            type='info')
        return self.request.response.redirect(url)

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.panel')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data


class PanelSubHeadingEditForm(form.SchemaEditForm):
    grok.context(IPanelPage)
    grok.require('cmf.AddPortalContent')
    grok.name('panel-subheading')

    schema = IPanelSubHeading
    ignoreContext = True
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
        parent = aq_parent(context)
        row = self.traverse_subpath[0]
        url = '{0}/@@panelblock-editor/{1}'.format(parent.absolute_url(), row)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content panel factory has been cancelled."),
            type='info')
        return self.request.response.redirect(url)

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.panel')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data


class PanelAbstractEditForm(form.SchemaEditForm):
    grok.context(IPanelPage)
    grok.require('cmf.AddPortalContent')
    grok.name('panel-abstract')

    schema = IPanelAbstract
    ignoreContext = True
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
        parent = aq_parent(context)
        row = self.traverse_subpath[0]
        url = '{0}/@@panelblock-editor/{1}'.format(parent.absolute_url(), row)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content panel factory has been cancelled."),
            type='info')
        return self.request.response.redirect(url)

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.panel')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data


class PanelTextEditForm(form.SchemaEditForm):
    grok.context(IPanelPage)
    grok.require('cmf.AddPortalContent')
    grok.name('panel-text')

    schema = IPanelText
    ignoreContext = True
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
        parent = aq_parent(context)
        row = self.traverse_subpath[0]
        url = '{0}/@@panelblock-editor/{1}'.format(parent.absolute_url(), row)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content panel factory has been cancelled."),
            type='info')
        return self.request.response.redirect(url)

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.panel')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data


class PanelRichTextEditForm(form.SchemaEditForm):
    grok.context(IPanelPage)
    grok.require('cmf.AddPortalContent')
    grok.name('panel-richtext')

    schema = IPanelRichText
    ignoreContext = True
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
        setattr(item, 'text', data['text'])
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


class PanelImageEditForm(form.SchemaEditForm):
    grok.context(IPanelPage)
    grok.require('cmf.AddPortalContent')
    grok.name('panel-image')

    schema = IPanelImage
    ignoreContext = True
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
        parent = aq_parent(context)
        row = self.traverse_subpath[0]
        url = '{0}/@@panelblock-editor/{1}'.format(parent.absolute_url(), row)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content panel factory has been cancelled."),
            type='info')
        return self.request.response.redirect(url)

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.panel')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data


class IContentPanelEdit(form.Schema):

    title = schema.TextLine(
        title=_(u"Content panel title"),
        required=True,
    )
    description = schema.Text(
        title=_(u"Teaser"),
        description=_(u"Short and visualy highlighted teaser message"),
        required=False,
    )
    icon_klass = schema.TextLine(
        title=_(u"Content panel icon class"),
        description=_(u"Add an icon class from font awesome site"),
        required=False,
    )
    image = NamedBlobImage(
        title=_(u"Panel Icon Image"),
        description=_(u"Upload panel icon image suitable in size and "
                      u"dimension for the usecase"),
        required=False,
    )
    text = RichText(
        title=_(u"Body Text"),
        description=_(u"Please enter rich formatted text. But keep it short "
                      u"and suitable for a content panel"),
        required=False,
    )


class IContentPanelLinkEdit(form.Schema):

    linked_item = RelationChoice(
        title=_(u"Link target"),
        source=ObjPathSourceBinder(
            portal_type=[
                'ade25.panelpage.contentpage',
                'ade25.panelpage.sectionfolder']
        ),
        required=False,
    )
    show_contentlisting = schema.Bool(
        title=_(u"Enable content listing"),
        description=_(u"List contents of link target"),
        required=False
    )


class ContentPanelEditForm(form.SchemaEditForm):
    grok.context(IContentPanel)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-panel')

    schema = IContentPanelEdit
    ignoreContext = False
    css_class = 'app-form'

    label = _(u"Edit content panel")

    def updateActions(self):
        super(ContentPanelEditForm, self).updateActions()
        self.actions['save'].addClass("btn btn-primary")
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
            _(u"Content panel factory has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.contentpanel')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.contentpanel')
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
            _(u"The panel has successfully been updated"),
            type='info')
        next_url = context.absolute_url()
        parent = aq_parent(context)
        if IPanelManager.providedBy(parent):
            next_url = parent.absolute_url()
        return self.request.response.redirect(next_url)


class ContentPanelLinkEditForm(form.SchemaEditForm):
    grok.context(IContentPanel)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-panel-link')

    schema = IContentPanelLinkEdit
    ignoreContext = False
    css_class = 'app-form'

    label = _(u"Edit content panel")

    def updateActions(self):
        super(ContentPanelLinkEditForm, self).updateActions()
        self.actions['save'].addClass("btn btn-primary")
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
            _(u"Content panel factory has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.panelpage.contentpanel')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        data['linked_item'] = uuidToObject(data['linked_item'])
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        linked_item = data['linked_item']
        setattr(context, 'linked_item', linked_item.UID())
        setattr(context, 'show_contentlisting', data['show_contentlisting'])
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The panel has successfully been updated"),
            type='info')
        next_url = context.absolute_url()
        parent = aq_parent(context)
        if IPanelManager.providedBy(parent):
            next_url = parent.absolute_url()
        return self.request.response.redirect(next_url)


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
