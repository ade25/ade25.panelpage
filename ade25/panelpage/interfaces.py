from zope import schema
from zope.interface import Interface
from plone.directives import form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage

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
