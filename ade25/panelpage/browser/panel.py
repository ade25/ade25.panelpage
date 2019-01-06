# -*- coding: utf-8 -*-
"""Module providing panel views"""
import json
import os
import time
import datetime
import uuid as uuid_tool

from Acquisition import aq_inner
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from plone import api

from ade25.base.utils import get_filesystem_template
from ade25.panelpage import MessageFactory as _

from plone.i18n.normalizer import IIDNormalizer
from zope.component import queryUtility


class PanelDefaultSettings(BrowserView):
    """ Base widget used as placeholder """

    def __call__(self):
        return self.render()

    @staticmethod
    def build_default_configuration():
        """ Build default panel configuration

        Addon packages are expected to add their custom widget configuration
        requirements to the registry during import and initialization and these
        will be used as panel setting keys
        """
        template = get_filesystem_template(
            'content-panel.json',
            os.path.dirname(os.path.dirname(__file__)),
            data={
                "id": str(uuid_tool.uuid4()),
                "timestamp": str(int(time.time())),
                "created": datetime.datetime.now().isoformat(),
                "widget_id": str(uuid_tool.uuid4())
            }
        )
        try:
            panel_setting_template = json.loads(template)
            settings = json.dumps(panel_setting_template)
        except ValueError:
            settings = '{}'
        return safe_unicode(settings)

    def render(self):
        msg = _(u"Panel configuration data not available")
        data = {
            'success': False,
            'message': msg
        }
        settings = self.build_default_configuration()
        if settings:
            data = settings
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return data


class ContentPanel(BrowserView):
    """ Basic content panel view  """

    def __call__(self, data=None, mode="view", **kw):
        self.params = {"mode": mode, "data": data}
        return self.render()

    def render(self):
        return self.index()

    @staticmethod
    def can_edit():
        return not api.user.is_anonymous()

    @staticmethod
    def normalizer():
        return queryUtility(IIDNormalizer)

    def card_subject_classes(self, item):
        context = item
        subjects = context.Subject()
        class_list = [
            "app-card-tag--{0}".format(self.normalizer().normalize(keyword))
            for keyword in subjects
        ]
        return class_list

    def card_css_classes(self, item):
        class_list = self.card_subject_classes(item)
        if class_list:
            return " ".join(class_list)
        else:
            return "app-card-tag--all"

    @staticmethod
    def has_image(context):
        try:
            lead_img = context.image
        except AttributeError:
            lead_img = None
        if lead_img is not None:
            return True
        return False

    def widget_content(self):
        context = aq_inner(self.context)
        panel_data = self.params["data"]
        details = {

        }
        import pdb; pdb.set_trace()
        return details


class ContentPanelEdit(BrowserView):

    def __call__(self, data=None, mode="view", **kw):
        self.params = {"mode": mode, "data": data}
        return self.render()

    def render(self):
        return self.index()

    @staticmethod
    def can_edit():
        return not api.user.is_anonymous()

