# -*- coding: utf-8 -*-
"""Module providing panel views"""
import json
import os
import time
import datetime
import uuid as uuid_tool

from AccessControl import Unauthorized
from Acquisition import aq_inner
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from ade25.panelpage.interfaces import IPanelTool
from plone import api

from ade25.base.utils import get_filesystem_template
from ade25.panelpage import MessageFactory as _

from plone.i18n.normalizer import IIDNormalizer
from zope.component import queryUtility, getUtility, getMultiAdapter


class PanelDefaultSettings(BrowserView):
    """ Base widget used as placeholder """

    def __call__(self, widget_type="base"):
        self.widget_type = widget_type
        return self.render()

    def build_default_configuration(self):
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
                "widget_id": str(uuid_tool.uuid4()),
                "widget_type": self.widget_type
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

    def __call__(self,
                 identifier=None,
                 section='main',
                 panel=None,
                 **kw):
        self.params = {
            'panel_page_identifier': identifier,
            'panel_page_section': self.request.get('section', section),
            'panel_page_item': self.request.get('index', panel)
        }
        return self.render()

    def render(self):
        return self.index()

    @staticmethod
    def can_edit():
        return not api.user.is_anonymous()

    @property
    def settings(self):
        return self.params

    @property
    def panel_tool(self):
        tool = getUtility(IPanelTool)
        return tool

    def stored_panel(self):
        context = aq_inner(self.context)
        identifier = self.settings['panel_page_identifier']
        if not identifier:
            identifier = context.UID()
        panel_data = self.panel_tool.read(
            identifier,
            section=self.settings['panel_page_section'],
            key=self.settings['panel_page_item']
        )
        return panel_data

    def content_panel(self):
        content_panel = json.loads(self.stored_panel())
        return content_panel


class ContentPanelCreate(BrowserView):

    def __call__(self,
                 index=0,
                 section="view",
                 **kw):
        self.params = {
            "panel_page_item": self.request.get('index', 0),
            "panel_page_section": self.request.get('section', 'main')
        }
        self.params.update(kw)
        return self.render()

    def update(self):
        self.errors = dict()
        unwanted = ('_authenticator', 'form.button.Submit')
        required = ('selector_display_type', )
        if 'form.button.Submit' in self.request:
            authenticator = getMultiAdapter((self.context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            form = self.request.form
            form_data = {}
            form_data.update(self.params)
            form_errors = {}
            error_idx = 0
            for value in form:
                if value not in unwanted:
                    form_data[value] = safe_unicode(form[value])
                    if not form[value] and value in required:
                        form_errors[value] = self.required_field_error()
                        error_idx += 1
                    else:
                        error = {
                            'active': False,
                            'msg': form[value]
                        }
                        form_errors[value] = error
            if error_idx > 0:
                self.errors = form_errors
            else:
                self._create_panel(form)

    def render(self):
        self.update()
        return self.index()

    @staticmethod
    def can_edit():
        return not api.user.is_anonymous()

    @property
    def settings(self):
        return self.params

    @property
    def panel_tool(self):
        tool = getUtility(IPanelTool)
        return tool

    @staticmethod
    def required_field_error():
        translation_service = api.portal.get_tool(name="translation_service")
        error = {}
        error_msg = _(u"This field is required")
        error['active'] = True
        error['msg'] = translation_service.translate(
            error_msg,
            'ade25.contacts',
            target_language=api.portal.get_default_language()
        )
        return error

    def _create_panel(self, form_data):
        context = aq_inner(self.context)
        i18n_service = api.portal.get_tool(name="translation_service")
        success_message = _(u"Content Panel created")
        message = i18n_service.translate(
            success_message,
            'hph.lectures',
            target_language=api.portal.get_default_language()
        )
        selected_widget_type = 'base'
        for record in form_data:
            if record.startswith('widget'):
                selected_widget_type = record.split('.')[1]
        panel_data = self.panel_tool.create(
            context.UID(),
            section=form_data['panel_page_section'],
            widget_type=selected_widget_type,
            widget_position=form_data['panel_page_item']
        )
        next_url = '{0}/@@panel-edit?section={1}&index={2}'.format(
            context.absolute_url(),
            form_data['panel_page_section'],
            form_data['panel_page_item']
        )
        api.portal.show_message(message=message,
                                request=self.request,
                                type='info')
        return self.request.response.redirect(next_url)
