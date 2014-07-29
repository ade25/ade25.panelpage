from zope import schema
from zope.interface import Interface
from plone.directives import form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from plone.formwidget.querystring.widget import QueryStringFieldWidget

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

    textline = schema.TextLine(
        title=_(u"Alias"),
        required=False,
    )


class IPanelListing(form.Schema):

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
