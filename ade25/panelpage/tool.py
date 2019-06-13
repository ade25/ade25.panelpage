# -*- coding: utf-8 -*-
"""Module providing genearal toolset for panel management"""
import datetime
import json
import os
import uuid as uuid_tool

import time

from ade25.base.utils import get_filesystem_template
from babel.dates import format_datetime
from Products.CMFPlone.utils import safe_unicode
from collective.beaker.interfaces import ISession
from future.backports.email.utils import format_datetime
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from plone.event.utils import pydt
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.lifecycleevent import modified
from zope.schema import getFieldsInOrder
# from collective.beaker.interfaces import ISession

SESSION_KEY = 'Uh53dAfH2JPzI/lIhBvN72RJzZVv6zk5'


class PanelTool(object):
    """ Utility providing CRUD operation for panel pages """

    def create(self,
               uuid=None,
               section='main',
               widget_type='base',
               widget_position=0):
        item = api.content.get(UID=uuid)
        widget_data = self.create_record(uuid, widget_type)
        field_name = 'contentPanels{0}'.format(
            section.capitalize(),
        )
        records = getattr(item, field_name, list())
        if not records:
            # Handle initial panel setup
            records = list()
        try:
            records.insert(widget_position, widget_data)
        except TypeError:
            insert_position = int(widget_position)
            records.insert(insert_position, widget_data)
        setattr(item, field_name, records)
        modified(item)
        item.reindexObject(idxs='modified')
        return widget_data

    # @memoize
    def read(self, uuid, section='main', key=None):
        item = api.content.get(UID=uuid)
        field_name = 'contentPanels{0}'.format(
            section.capitalize(),
        )
        stored = getattr(item, field_name, None)
        data = list()
        if stored is not None:
            data = stored
        if key is not None:
            data = stored[int(key)]
        return data

    def update(self, uuid, data, section='main', key=None):
        item = api.content.get(UID=uuid)
        field_name = 'contentPanels{0}'.format(
            section.capitalize(),
        )
        stored = getattr(item, field_name, None)
        if key is not None:
            updated = stored
            updated[int(key)] = data
            setattr(item, field_name, updated)
            modified(item)
            item.reindexObject(idxs='modified')
        return data

    def delete(self, uuid, section='main', key=None):
        item = api.content.get(UID=uuid)
        field_name = 'contentPanels{0}'.format(
            section.capitalize(),
        )
        stored = getattr(item, field_name, None)
        if key is not None:
            updated = stored
            del updated[int(key)]
            setattr(item, field_name, updated)
            modified(item)
            item.reindexObject(idxs='modified')
        return uuid

    def create_record(self, uuid=None, widget_type=None):
        record = self.build_default_configuration(uuid, widget_type)
        return record

    @staticmethod
    def build_default_configuration(uuid, widget_type):
        """ Build default panel configuration

        Addon packages are expected to add their custom widget configuration
        requirements to the registry during import and initialization and these
        will be used as panel setting keys
        """
        template = get_filesystem_template(
            'content-panel.json',
            os.path.dirname(__file__),
            data={
                "id": str(uuid_tool.uuid4()),
                "context": uuid,
                "timestamp": str(int(time.time())),
                "created": datetime.datetime.now().isoformat(),
                "widget_id": str(uuid_tool.uuid4()),
                "widget_type": widget_type
            }
        )
        try:
            panel_setting_template = json.loads(template)
            settings = json.dumps(panel_setting_template)
        except ValueError:
            settings = '{}'
        return safe_unicode(settings)

    @staticmethod
    def safe_encode(value):
        """Return safe unicode version of value.
        """
        su = safe_unicode(value)
        return su.encode('utf-8')

    @staticmethod
    def time_stamp(date_value):
        date = pydt(date_value)
        timestamp = {
            'day': format_datetime(date, 'dd', locale='de'),
            'day_name': format_datetime(date, 'EEEE', locale='de'),
            'month': date.strftime("%m"),
            'year': date.strftime("%Y"),
            'hour': date.strftime('%H'),
            'minute': date.strftime('%M'),
            'time': format_datetime(date, 'H:mm', locale='de'),
            'date': date,
            'date_short': format_datetime(date, 'short', locale='de')
        }
        return timestamp


class PanelEditorTool(object):
    """ Panel editor session storage tool

        Store selected panel configuration inside anonymous session
        to provide dynamically built add and edit forms for content
        panels and widgets
    """

    @staticmethod
    def get(key=None):
        """ Create module filter session """
        portal = api.portal.get()
        session_id = 'ade25.panelpage.editor.{0}'.format(
            '.'.join(portal.getPhysicalPath())
        )
        if key:
            session_id = 'ade25.panelpage.editor.{0}'.format(key)
        session = ISession(getRequest())
        if session_id not in session:
            session[session_id] = dict()
            session.save()
        return session[session_id]

    @staticmethod
    def destroy(key=None):
        """ Destroy module filter session """
        portal = api.portal.get()
        session_id = 'ade25.panelpage.editor.{0}'.format(
            '.'.join(portal.getPhysicalPath())
        )
        if key:
            session_id = 'ade25.panelpage.editor.{0}'.format(key)
        session = ISession(getRequest())
        if session_id in session:
            del session[session_id]
            session.save()

    def add(self, key, data=None):
        """
            Add item to survey session
        """
        session = self.get()
        item = self.update(key, data)
        if not item:
            session[key] = data
            return session[key]

    def update(self, key, data):
        session = self.get()
        item_id = key
        if item_id in session:
            session[item_id] = data
            return session[item_id]
        return None

    def remove(self, key):
        session = self.get()
        if key in session:
            del session[key]
            return key
