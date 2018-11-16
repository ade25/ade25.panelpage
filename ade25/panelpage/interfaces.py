# -*- coding: UTF-8 -*-
from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer


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
