# -*- coding: UTF-8 -*-
from Acquisition import aq_inner
from five import grok
from plone import api
from zope import schema
from zope.component import getMultiAdapter

from plone.dexterity.content import Item
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable

from ade25.panelpage import MessageFactory as _


class IPanel(form.Schema, IImageScaleTraversable):
    """
    A single content panel or box
    """
    title = schema.TextLine(
        title=_(u"Content Panel Title"),
        required=True,
    )
    klass = schema.TextLine(
        title=_(u"CSS Class"),
        required=False,
    )
    form.omitted('component')
    component = schema.TextLine(
        title=_(u"Component"),
        required=False,
    )


class Panel(Item):
    grok.implements(IPanel)
    pass


class View(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('view')

    def render_item(self):
        context = aq_inner(self.context)
        component = getattr(context, 'component')
        viewname = '@@panel-{0}'.format(component)
        template = context.restrictedTraverse(viewname)()
        return template


class ContentView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('content-view')


class HeadingView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('panel-heading')


class SubheadingView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('panel-subheading')


class AbstractView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('panel-abstract')


class TextView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('panel-text')


class RichTextView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('panel-richtext')


class ImageView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('panel-image')


class PanelListingView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('panel-listing')

    def update(self):
        self.query = self._get_stored_query()

    def _get_stored_query(self):
        context = aq_inner(self.context)
        return getattr(context, 'query')

    def dynamic_contents(self, batch=True, b_start=0, b_size=None,
                         sort_on=None, limit=None, brains=False):
        context = aq_inner(self.context)
        querybuilder = getMultiAdapter((self.context, self.context.REQUEST),
                                       name='querybuilderresults')
        sort_order = 'reverse' if context.sort_reversed else 'ascending'
        if not b_size:
            b_size = context.item_count
        if not sort_on:
            sort_on = context.sort_on
        if not limit:
            limit = context.limit

        query = self.query
        if query:
            has_path_criteria = any(
                (criteria['i'] == 'path')
                for criteria in query
            )
            if not has_path_criteria:
                # Make a copy of the query to avoid modifying it
                query = list(self.query)
                query.append({
                    'i': 'path',
                    'o': 'plone.app.querystring.operation.string.path',
                    'v': '/',
                })

        return querybuilder(
            query=query, batch=batch, b_start=b_start, b_size=b_size,
            sort_on=sort_on, sort_order=sort_order,
            limit=limit, brains=brains
        )


class AliasView(grok.View):
    grok.context(IPanel)
    grok.require('zope2.View')
    grok.name('panel-alias')

    def resolve_item(self, uuid):
        return api.content.get(UID=uuid)
