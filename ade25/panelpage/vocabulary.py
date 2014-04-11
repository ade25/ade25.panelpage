from five import grok
from zope.schema. interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from ade25.panelpage import MessageFactory as _


class AvailableLayoutsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        TYPES = {_(u"1 Col"): '12',
                 _(u"2 Cols 1:1"): '6',
                 _(u"2 Cols 1:2"): '4-8',
                 _(u"2 Cols 2:1"): '8-4',
                 _(u"2 Cols 3:1"): '9-3',
                 _(u"3 Cols"): '4',
                 _(u"4 Cols"): '3'}
        return SimpleVocabulary([SimpleTerm(value, title=title)
                                for title, value
                                in TYPES.iteritems()])
grok.global_utility(AvailableLayoutsVocabulary,
                    name=u"ade25.panelpage.AvailableLayouts")
