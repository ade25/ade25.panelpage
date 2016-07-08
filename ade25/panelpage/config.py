# -*- coding: utf-8 -*-
""" Tool configuration """

from ade25.panelpage import MessageFactory as _


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
        'textline': 'ion-ios-document-outline',
        'heading': 'ion-ios-document-outline',
        'subheading': 'ion-ios-document-outline',
        'abstract': 'ion-ios-document-outline',
        'text': 'ion-ios-document-outline',
        'richtext': 'ion-ios-document-outline',
        'image': 'ion-ios-image-outline',
        'listing': 'ion-ios-images-outline',
        'box': 'ion-filing-outline',
        'alias': 'ion-ios-browsers',
        'placeholder': 'ion-ios-create-outline'
    }
    return matrix
