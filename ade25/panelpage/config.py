# -*- coding: utf-8 -*-

from ade25.panelpage import MessageFactory as _

""" Tool configuration """


def panel_components():
    components = [
        'heading',
        'subheading',
        'abstract',
        'text',
        'richtext',
        'image',
        'alias',
        'listing'
    ]
    return components


def pretty_components():
    components = {
        'heading': _(u"Heading"),
        'subheading': _(u"Subheading"),
        'abstract': _(u"Abstract"),
        'text': _(u"Plaintext"),
        'richtext': _(u"Richtext"),
        'image': _(u"Image"),
        'alias': _(u"Alias"),
        'listing': _(u"Listing")
    }
    return components


def component_icons():
    """ Asumes ionicons icon file """
    matrix = {
        'textline': 'ion-document',
        'heading': 'ion-document',
        'subheading': 'ion-document',
        'abstract': 'ion-document-text',
        'text': 'ion-document-text',
        'richtext': 'ion-document-text',
        'image': 'ion-image',
        'listing': 'ion-ios7-albums-outline',
        'box': 'ion-filing',
        'alias': 'ion-ios7-download',
        'placeholder': 'ion-ios7-circle-outline'
    }
    return matrix
