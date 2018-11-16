# -*- coding: utf-8 -*-
"""Module providing panel views"""
import json
import os
import time
import datetime
import uuid as uuid_tool

from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from ade25.base.utils import get_filesystem_template

from ade25.panelpage import MessageFactory as _


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
        return json.dumps(data)
