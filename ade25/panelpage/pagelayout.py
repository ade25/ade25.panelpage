from zope import schema
from zope.interface import alsoProvides
from plone.directives import form

from plone.autoform.interfaces import IFormFieldProvider

from ade25.panelpage import MessageFactory as _


class IPanelPageLayout(form.Schema):
    """ Behavior storing panelpage block order """

    form.fieldset(
        'layout',
        label=_(u"Page Layout"),
        fields=['panelPageLayout']
    )
    #form.mode(panelPageLayout='hidden')
    panelPageLayout = schema.List(
        title=_("Panel Page Layout"),
        value_type=schema.TextLine(
            title=_(u"Content Block UID"),
        ),
        required=False,
    )

alsoProvides(IPanelPageLayout, IFormFieldProvider)
