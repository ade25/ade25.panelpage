from Acquisition import aq_inner
from five import grok
from zope import schema
from zope.component import getMultiAdapter
from plone.dexterity.content import Item

from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable

from plone.formwidget.querystring.widget import QueryStringFieldWidget

from ade25.panelpage import MessageFactory as _


class IListingPanel(form.Schema, IImageScaleTraversable):
    """
    A single content panel or box
    """
    title = schema.TextLine(
        title=_(u"Content panel title"),
        required=True,
    )
    klass = schema.TextLine(
        title=_(u"CSS Class"),
        required=False,
    )
    subitems = schema.Bool(
        title=_(u"Display subitems"),
        description=_(u"Use this setting to automatically list all subcontents"
                      u" of this context. All custom query selections made"
                      u" will be ignored"),
        required=False
    )
    form.widget(query=QueryStringFieldWidget)
    query = schema.List(
        title=_(u"Search terms"),
        description=_(u"Define the search terms for the items you want to list"
                      u" by choosing what to match on. The list of results"
                      u"will be dynamically updated"),
        value_type=schema.Dict(
            value_type=schema.Field(),
            key_type=schema.TextLine()
        ),
        required=False
    )
    sort_on = schema.TextLine(
        title=_(u'label_sort_on', default=u'Sort on'),
        description=_(u"Sort the collection on this index"),
        required=False,
    )

    sort_reversed = schema.Bool(
        title=_(u'label_sort_reversed', default=u'Reversed order'),
        description=_(u'Sort the results in reversed order'),
        required=False,
    )

    limit = schema.Int(
        title=_(u'Limit'),
        description=_(u'Limit Search Results'),
        required=False,
        default=1000,
    )

    item_count = schema.Int(
        title=_(u'label_item_count', default=u'Item count'),
        description=_(u'Number of items that will show up in one batch.'),
        required=False,
        default=30,
    )


class ListingPanel(Item):
    grok.implements(IListingPanel)
    pass


class View(grok.View):
    grok.context(IListingPanel)
    grok.require('zope2.View')
    grok.name('view')

    def render_item(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@content-view')()
        return template


class ContentView(grok.View):
    grok.context(IListingPanel)
    grok.require('zope2.View')
    grok.name('content-view')

    def results(self, batch=True, b_start=0, b_size=None,
                sort_on=None, limit=None, brains=False):
        querybuilder = getMultiAdapter((self.context, self.context.REQUEST),
                                       name='querybuilderresults')
        sort_order = 'reverse' if self.sort_reversed else 'ascending'
        if not b_size:
            b_size = self.item_count
        if not sort_on:
            sort_on = self.sort_on
        if not limit:
            limit = self.limit

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
