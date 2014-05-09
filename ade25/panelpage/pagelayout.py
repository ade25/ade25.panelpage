from Acquisition import aq_inner
from five import grok
from plone import api
from zope import schema

from zope.lifecycleevent import modified
from zope.interface import alsoProvides
from plone.directives import form
from plone.keyring import django_random

from plone.autoform.interfaces import IFormFieldProvider
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.statusmessages.interfaces import IStatusMessage

from ade25.panelpage.contentblock import IContentBlock
from ade25.panelpage.panelpage import IPanelPage


from ade25.panelpage import MessageFactory as _


class IPanelPageLayout(form.Schema):
    """ Behavior storing panelpage block order """

    #form.mode(panelPageLayout='hidden')
    panelPageLayout = schema.List(
        title=_("Panel Page Layout"),
        value_type=schema.TextLine(
            title=_(u"Content Page Layout"),
        ),
        required=False,
    )

alsoProvides(IPanelPageLayout, IFormFieldProvider)


class MigrateLayout(grok.View):
    grok.context(INavigationRoot)
    grok.require('cmf.ManagePortal')
    grok.name('migrate-layout')

    def render(self):
        pages = self._panel_pages()
        updated = self._migrate_items(pages)
        msg = '{0} blocks migrated to panels'.format(updated)
        IStatusMessage(self.request).addStatusMessage(msg, type='info')
        url = self.context.absolute_url()
        return self.request.response.redirect(url)

    def _panel_pages(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IPanelPage.__identifier__,)
        return items

    def _migrate_items(self, pages):
        context = aq_inner(self.context)
        catalog = api.portal.get_tool(name="portal_catalog")
        idx = 0
        for page in pages:
            grid = list()
            obj = page.getObject()
            blocks = catalog(object_provides=IContentBlock.__identifier__,
                             path=dict(query='/'.join(obj.getPhysicalPath()),
                                       depth=1))
            for b in blocks:
                cb = b.getObject()
                title_row = self._build_gridrow(cb, 'title')
                grid.append(title_row)
                idx += 1
                if cb.Description:
                    abstract_row = self._build_gridrow(cb, 'description')
                    grid.append(abstract_row)
                    idx += 1
                if cb.text:
                    text_row = self._build_gridrow(cb, 'text')
                    grid.append(text_row)
                    idx += 1
        context = aq_inner(self.context)
        setattr(context, 'panelPageLayout', grid)
        modified(context)
        context.reindexObject(idxs='modified')
        return idx

    def _build_gridrow(self, cb, key):
        value = getattr(cb, key)
        token = django_random.get_random_string(length=24)
        component = u"text"
        if key == 'headline':
            component = u"heading"
        if key == 'description':
            component = u"abstract"
        uid = self._create_panel(component, key, value)
        row = {
            'id': token,
            'title': '{0}: {1}'.format(component, cb.Title),
            'status': 'visible',
            'klass': 'pp-row-default',
            'panels': [
                {
                    'uuid': uid,
                    'component': component,
                    'grid-col': 12,
                    'klass': 'panel-column panel-column-{0}'.format(component)
                }
            ]
        }
        return row

    def _create_panel(self, component, key, value):
        context = aq_inner(self.context)
        token = django_random.get_random_string(length=24)
        item = api.content.create(
            type='ade25.panelpage.panel',
            id=token,
            title=token,
            container=context,
            safe_id=True
        )
        setattr(item, 'component', component)
        if key == 'description':
            setattr(item, 'textblock', value)
        if key == 'headline':
            setattr(item, 'textline', value)
        else:
            setattr(item, key, value)
        modified(item)
        item.reindexObject(idxs='modified')
        uuid = api.content.get_uuid(obj=item)
        return uuid
