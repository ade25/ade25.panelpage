# -*- coding: utf-8 -*-
"""Module providing content type cleanup"""
from Acquisition import aq_inner
from Products.Five import BrowserView
from plone import api
from plone.protect.utils import addTokenToUrl
from zope.component import getMultiAdapter
from zope.lifecycleevent import modified
from Products.CMFPlone import utils


class RemoveLegacyContent(BrowserView):
    """ Migrate panel page content

    Query the catalog for legacy content impending removal
    """

    def __call__(self):
        self.has_legacy_content = len(self.legacy_content()) > 0
        return self.render()

    def render(self):
        return self.index()

    @staticmethod
    def legacy_content():
        legacy_content_types = [
            'ade25.panelpage.panel',
            'ade25.panelpage.panelmanager',
            'ade25.panelpage.contentblock',
        ]
        items = api.content.find(
            context=api.portal.get(),
            portal_type=legacy_content_types,
            sort_on='effective',
            sort_order='reverse'
        )
        return items

    def content_items(self):
        results = list()
        for brain in self.legacy_content():
            entry = {
                'uid': brain.UID,
                'key': '/'.join(brain.getPath().split('/')[:-1]),
                'path': '/'.join(brain.getPath().split('/')),
                'url': brain.getURL(),
                'title': utils.safe_unicode(brain.Title),
                'portal_type': brain.portal_type
            }
            results.append(entry)
        return results

    def content_items_counter(self):
        return len(self.content_items())

    def cleanup_action(self):
        context = aq_inner(self.context)
        action_url = '{0}/@@panel-page-content-migration-runner'.format(
            context.absolute_url()
        )
        return addTokenToUrl(action_url)


class RemoveLegacyContentRunner(BrowserView):
    """ Blog migration runner """

    def __call__(self):
        return self.render()

    def render(self):
        context = aq_inner(self.context)
        self._cleanup_legacy_content()
        api.portal.show_message(
            message='Panel Page legacy content successfully removed.',
            request=self.request
        )
        return self.request.response.redirect(context.absolute_url())

    @staticmethod
    def _cleanup_legacy_content():
        legacy_content_types = [
            'ade25.panelpage.panel',
            'ade25.panelpage.panelmanager',
            'ade25.panelpage.contentblock',
        ]
        items = api.content.find(
            context=api.portal.get(),
            portal_type=legacy_content_types,
            sort_on='effective',
            sort_order='reverse'
        )
        for candidate in items:
            api.content.delete(
                candidate.getObject(),
                check_linkintegrity=False
            )
