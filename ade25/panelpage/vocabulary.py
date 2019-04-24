# -*- coding: utf-8 -*-
"""Module providing panel page vocabularies"""
from binascii import b2a_qp

from zope.interface import implementer
from zope.schema. interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from ade25.panelpage import MessageFactory as _


@implementer(IVocabularyFactory)
class ContentPanelLayoutVocabularyFactory(object):

    def __call__(self, context):
        widgets = self.get_display_options()
        terms = [
            self.generate_simple_term(widget_key, widget_term)
            for widget_key, widget_term in widgets.items()
        ]
        return SimpleVocabulary(terms)

    @staticmethod
    def generate_simple_term(widget, widget_term):
        term = SimpleTerm(
            value=widget,
            token=b2a_qp(widget.encode('utf-8')),
            title=_(widget_term)
        )
        return term

    @staticmethod
    def get_display_options():
        display_options = {
            'c-panel--default': _(u'Full width container'),
            'c-panel--centered': _(u'Centered constrained container'),
            'c-panel--container-centered':
                _(u'Full width container with centered constrained content'),
        }
        return display_options


ContentPanelLayoutVocabulary = ContentPanelLayoutVocabularyFactory()


@implementer(IVocabularyFactory)
class ContentPanelDesignVocabularyFactory(object):

    def __call__(self, context):
        widgets = self.get_display_options()
        terms = [
            self.generate_simple_term(widget_key, widget_term)
            for widget_key, widget_term in widgets.items()
        ]
        return SimpleVocabulary(terms)

    @staticmethod
    def generate_simple_term(widget, widget_term):
        term = SimpleTerm(
            value=widget,
            token=b2a_qp(widget.encode('utf-8')),
            title=_(widget_term)
        )
        return term

    @staticmethod
    def get_display_options():
        display_options = {
            'c-panel--bg-default': _(u'Default'),
            'c-panel--bg-primary': _(u'Primary Background'),
            'c-panel--bg-secondary': _(u'Secondary Background')
        }
        return display_options


ContentPanelDesignVocabulary = ContentPanelDesignVocabularyFactory()


@implementer(IVocabularyFactory)
class ContentPanelDisplayVocabularyFactory(object):

    def __call__(self, context):
        widgets = self.get_display_options()
        terms = [
            self.generate_simple_term(widget_key, widget_term)
            for widget_key, widget_term in widgets.items()
        ]
        return SimpleVocabulary(terms)

    @staticmethod
    def generate_simple_term(widget, widget_term):
        term = SimpleTerm(
            value=widget,
            token=b2a_qp(widget.encode('utf-8')),
            title=_(widget_term)
        )
        return term

    @staticmethod
    def get_display_options():
        display_options = {
            'u-display--none': _(u'Hidden'),
            'u-display--block|u-display-sm--none': _(u'Hidden from 576px'),
            'u-display--block|u-display-md--none': _(u'Hidden from 768px'),
            'u-display--block|u-display-lg--none': _(u'Hidden from 992px'),
            'u-display--block|u-display-xl--none': _(u'Hidden from 1200px'),
            'u-display--block|u-display-xxl--none': _(u'Hidden from 1400px'),
            'u-display--block|u-display-xxxl--none': _(u'Hidden from 1600px'),
            'u-display--block': _(u'Visible'),
            'u-display--none|u-display-sm--block': _(u'Visible from 576px'),
            'u-display--none|u-display-md--block': _(u'Visible from 768px'),
            'u-display--none|u-display-lg--block': _(u'Visible from 992px'),
            'u-display--none|u-display-xl--block': _(u'Visible from 1200px'),
            'u-display--none|u-display-xxl--block': _(u'Visible from 1400px'),
            'u-display--none|u-display-xxxl--block': _(u'Visible from 1600px'),
        }
        return display_options


ContentPanelDisplayVocabulary = ContentPanelDisplayVocabularyFactory()
