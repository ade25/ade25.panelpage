from five import grok
from zope.schema. interfaces import IVocabularyFactory
from zope.vocabulary import SimpleVocabulary
from zope.vocabulary import SimpleTerm

from ade25.panelpage import MessageFactory as _


class AvailableLayoutsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        TYPES = {_(u"Non-Profit Organization"): 'npo-org',
                 _(u"Profit Organization"): 'po-org'}
        return SimpleVocabulary([SimpleTerm(value, title=title)
                                for title, value
                                in TYPES.iteritems()])
grok.global_utility(AvailableLayoutsVocabulary,
                    name=u"ade25.panelpage.AvailableLayouts")
