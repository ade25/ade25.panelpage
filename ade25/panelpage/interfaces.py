# -*- coding: UTF-8 -*-
from plone.app.textfield import RichText
from plone.app.z3cform.widget import QueryStringFieldWidget
from plone.autoform import directives, form
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope import schema
from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

from ade25.panelpage import MessageFactory as _


class IAde25PanelPageLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class IPanelPage(Interface):
    """ Marker interface for panel page

    Type should ideally implement IDexterityContainer
    """


class IPanelPageEnabled(Interface):
    """ Marker interface for panel page enabled content

    Type should ideally implement IDexterityContainer
    """


class IPanelTool(Interface):
    """ Panel data processing

        General tool providing CRUD operations for assigning panel
        layout to content objects
    """

    def create(context):
        """ Create asset assignment data file

        The caller is responsible for passing a valid data dictionary
        containing the necessary details

        Returns JSON object

        @param uuid:        content object UID
        @param data:        predefined initial data dictionary
        """

    def read(context):
        """ Read stored data from object

        Returns a dictionary

        @param uuid:        object UID
        @param key:         (optional) dictionary item key
        """

    def update(context):
        """ Update stored data from object

        Returns a dictionary

        @param uuid:        object UID
        @param key:         (optional) dictionary item key
        @param data:        data dictionary
        """

    def delete(context):
        """ Delete stored data from object

        Returns a dictionary

        @param uuid:        caravan site object UID
        @param key:         (optional) dictionary item key
        """


class IPanelHeading(model.Schema):

    textline = schema.TextLine(
        title=_(u"Heading"),
        required=False,
    )


class IPanelSubHeading(model.Schema):

    textline = schema.TextLine(
        title=_(u"Subheading"),
        required=False,
    )


class IPanelAbstract(model.Schema):

    textblock = schema.Text(
        title=_(u"Abstract"),
        required=False,
    )


class IPanelText(model.Schema):

    textblock = schema.Text(
        title=_(u"Plaintext"),
        required=False,
    )


class IPanelRichText(model.Schema):

    text = RichText(
        title=_(u"Body"),
        required=False,
    )


class IPanelImage(model.Schema):

    image = NamedBlobImage(
        title=_(u"Panel Image"),
        description=_(u"Upload panel image suitable in size and "
                      u"dimension for the usecase"),
        required=False,
    )


class IPanelAlias(model.Schema):

    alias = schema.TextLine(
        title=_(u"Alias"),
        description=_(u"Enter UID of content aliase that can be obtained by "
                      u"appending @@UUID to a specific item URL"),
        required=False,
    )


class IPanelListing(model.Schema):

    contentlist = schema.Bool(
        title=_(u"Show Content Listing"),
        description=_(u"Enable to show a listing if this folder contents. All "
                      u"query settings will be ignored if selected"),
        required=False,
    )
    directives.widget('query', QueryStringFieldWidget)
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

    list_layout = schema.Choice(
        title=_(u"List Layout"),
        vocabulary=u"ade25.panelpage.AvailableLayouts",
        required=False,
        default=u'pp-list-base'
    )
