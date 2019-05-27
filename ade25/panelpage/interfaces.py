# -*- coding: UTF-8 -*-
from plone.autoform import directives as form, directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.theme.interfaces import IDefaultPloneLayer
from plone.supermodel import directives as model_directives

from zope import schema
from zope.interface import Interface
from zope.interface import provider

from ade25.panelpage import MessageFactory as _


class IAde25PanelPageLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class IPanelPage(Interface):
    """ Marker interface for panel page

    Type should ideally implement IDexterityContainer
    """


class IPanelPageEnabled(Interface):
    """ Marker interface for panel page enabled content

    Type should ideally implement IDexterityContainer
    """


class IPanelTool(Interface):
    """ Panel data processing

        General tool providing CRUD operations for assigning panel
        layout to content objects
    """

    def create(context):
        """ Create asset assignment data file

        The caller is responsible for passing a valid data dictionary
        containing the necessary details

        Returns JSON object

        @param uuid:        content object UID
        @param data:        predefined initial data dictionary
        """

    def read(context):
        """ Read stored data from object

        Returns a dictionary

        @param uuid:        object UID
        @param key:         (optional) dictionary item key
        """

    def update(context):
        """ Update stored data from object

        Returns a dictionary

        @param uuid:        object UID
        @param key:         (optional) dictionary item key
        @param data:        data dictionary
        """

    def delete(context):
        """ Delete stored data from object

        Returns a dictionary

        @param uuid:        caravan site object UID
        @param key:         (optional) dictionary item key
        """


class IContentPanelStorageSupport(Interface):
    """ Marker for content panel storage support """
    pass


@provider(IFormFieldProvider)
class IContentPanelSettings(Interface):
    """ Content Panel Settings """

    directives.mode(section='hidden')
    section = schema.TextLine(
        title=u'Page Section',
        required=False
    )
    directives.mode(panel='hidden')
    panel = schema.TextLine(
        title=u'Page Section Panel',
        required=False
    )
    directives.mode(identifier='hidden')
    identifier = schema.TextLine(
        title=u'Widget Identifier',
        required=False
    )

    model_directives.fieldset(
        'settings',
        label=u"Settings",
        fields=['widget_layout',
                'widget_design',
                'widget_display'
                ]
    )

    form.widget('widget_layout', klass='js-choices-selector')
    widget_layout = schema.Choice(
        title=_(u"Widget Layout"),
        description=_(u"Select layout for the content panel"),
        required=False,
        default='c-panel--default',
        vocabulary='ade25.panelpage.vocabularies.ContentPanelLayoutOptions'
    )
    form.widget('widget_design', klass='js-choices-selector')
    widget_design = schema.Choice(
        title=_(u"Widget Design"),
        description=_(u"Change predefined base style of the content panel"),
        required=False,
        default='c-panel--bg-default',
        vocabulary='ade25.panelpage.vocabularies.ContentPanelDesignOptions'
    )
    form.widget('widget_display', klass='js-choices-selector')
    widget_display = schema.Choice(
        title=_(u"Widget Display"),
        description=_(u"Select responsive behavior for widget"),
        required=False,
        default='u-display--block',
        vocabulary='ade25.panelpage.vocabularies.ContentPanelDisplayOptions'
    )
    custom_class = schema.TextLine(
        title=_(u"Additional CSS Classes"),
        description=_(u"Enter optional css classes that should be applied to "
                      u"the default widget class."),
        required=False
    )
