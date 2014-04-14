from five import grok
from zope.schema. interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from ade25.panelpage import MessageFactory as _


class AvailableLayoutsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        TYPES = {_(u"1 Cols"): '1',
                 _(u"2 Cols"): '2',
                 _(u"3 Cols"): '3',
                 _(u"4 Cols"): '4'}
        return SimpleVocabulary([SimpleTerm(value, title=title)
                                for title, value
                                in TYPES.iteritems()])
grok.global_utility(AvailableLayoutsVocabulary,
                    name=u"ade25.panelpage.AvailableLayouts")


class PanelPageComponentsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        TYPES = {
            _(u"Text"): 'text',
            _(u"Rich Text"): 'rich-text',
            _(u"Image"): 'image',
            _(u"Panel"): 'panel',
            _(u"Listing"): 'listing',
            _(u"Alias"): 'alias'
        }
        return SimpleVocabulary([SimpleTerm(value, title=title)
                                for title, value
                                in TYPES.iteritems()])
grok.global_utility(PanelPageComponentsVocabulary,
                    name=u"ade25.panelpage.PageComponents")
