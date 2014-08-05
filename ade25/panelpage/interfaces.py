# -*- coding: UTF-8 -*-
from plone.app.textfield import RichText
from plone.app.widgets.dx import QueryStringWidget
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from zope import schema
from zope.interface import Interface

from ade25.panelpage import MessageFactory as _


class IPanelPageEnabled(Interface):
    """ Marker interface for panel page enabled content

    Type should ideally implement IDexterityContainer
    """


class IPanelHeading(form.Schema):

    textline = schema.TextLine(
        title=_(u"Heading"),
        required=False,
    )


class IPanelSubHeading(form.Schema):

    textline = schema.TextLine(
        title=_(u"Subheading"),
        required=False,
    )


class IPanelAbstract(form.Schema):

    textblock = schema.Text(
        title=_(u"Abstract"),
        required=False,
    )


class IPanelText(form.Schema):

    textblock = schema.Text(
        title=_(u"Plaintext"),
        required=False,
    )


class IPanelRichText(form.Schema):

    text = RichText(
        title=_(u"Body"),
        required=False,
    )


class IPanelImage(form.Schema):

    image = NamedBlobImage(
        title=_(u"Panel Image"),
        description=_(u"Upload panel image suitable in size and "
                      u"dimension for the usecase"),
        required=False,
    )


class IPanelAlias(form.Schema):

    alias = schema.TextLine(
        title=_(u"Alias"),
        description=_(u"Enter UID of content aliase that can be obtained by "
                      u"appending @@UUID to a specific item URL"),
        required=False,
    )


class IPanelListing(form.Schema):

    form.widget('query', QueryStringWidget)
    query = schema.List(
        title=_(u'Search terms'),
        description=_(u"Define the search terms for the items you want "
                      u"to list by choosing what to match on. "
                      u"The list of results will be dynamically updated"),
        value_type=schema.Dict(
            value_type=schema.Field(),
            key_type=schema.TextLine()),
        required=False,
        missing_value=''
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

    textline = schema.TextLine(
        title=_(u"List Headline"),
        description=_(u"Add optional list headline"),
        required=False,
    )
