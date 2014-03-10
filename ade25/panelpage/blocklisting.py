from zope import schema
from zope.interface import alsoProvides
from plone.supermodel import model
from plone.directives import form

from plone.formwidget.querystring.widget import QueryStringFieldWidget

from plone.autoform.interfaces import IFormFieldProvider

from ade25.panelpage import MessageFactory as _


class IContentBlockListing(model.Schema):
    """ Behavior to store a query to provide content listings """
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

alsoProvides(IContentBlockListing, IFormFieldProvider)
