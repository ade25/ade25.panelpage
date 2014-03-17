from zope import schema
from zope.interface import alsoProvides
from plone.directives import form

from plone.autoform.interfaces import IFormFieldProvider

from ade25.panelpage import MessageFactory as _


class IStoredLayout(form.Schema):
    """ Behavior storing panelpage block order """

    form.fieldset(
        'layout',
        label=_(u"Stored Layout"),
        fields=['storedLayout']
    )
    storedLayout = schema.Choice(
        title=_("Stored Layout"),
        vocabulary=u"ade25.panelpage.AvailableLayouts",
        required=False,
    )

alsoProvides(IStoredLayout, IFormFieldProvider)
