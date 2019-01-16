# -*- coding: UTF-8 -*-
"""Behavior to provide additional content fields for panel items."""

from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.autoform import directives
from plone.formwidget.querystring.widget import QueryStringFieldWidget
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides

from ade25.panelpage import MessageFactory as _


class IPanelContent(model.Schema):
    """ Behavior storing panel content """

    # Hide behavior fields in autogenerated add and edit forms
    # form.omitted('textline', 'textblock', 'text', 'image' 'query', sort_on'
    # 'sort_reversed', 'limit', 'item_count')

    textline = schema.TextLine(
        title=_("Headline"),
        required=False,
    )
    textblock = schema.Text(
        title=_(u"Abstract"),
        required=False,
    )
    text = RichText(
        title=_(u"Body Text"),
        description=_(u"Please enter rich formatted text. But keep it short "
                      u"and suitable for a content panel"),
        required=False,
    )
    image = NamedBlobImage(
        title=_(u"Panel Icon Image"),
        description=_(u"Upload panel icon image suitable in size and "
                      u"dimension for the usecase"),
        required=False,
    )
    directives.widget(query=QueryStringFieldWidget)
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


alsoProvides(IPanelContent, IFormFieldProvider)
