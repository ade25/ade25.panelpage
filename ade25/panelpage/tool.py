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
from future.backports.email.utils import format_datetime
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from plone.event.utils import pydt
from zope.component import getUtility
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
        records = getattr(item, field_name, None)
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

    def update(self, uuid, component, data):
        item = api.content.get(UID=uuid)
        if 'textline' in data:
            setattr(item, 'textline', data['textline'])
        if 'textblock' in data:
            setattr(item, 'textblock', data['textblock'])
        else:
            fti = getUtility(IDexterityFTI,
                             name='ade25.panelpage.panel')
            schema = fti.lookupSchema()
            fields = getFieldsInOrder(schema)
            for key, value in fields:
                try:
                    new_value = data[key]
                    setattr(item, key, new_value)
                except KeyError:
                    continue
        modified(item)
        item.reindexObject(idxs='modified')
        return item

    def delete(self, uuid, section='main', key=None):
        item = api.content.get(UID=uuid)
        field_name = 'contentPanels{0}'.format(
            section.capitalize(),
        )
        stored = getattr(item, field_name, None)
        if key is not None:
            updated = dict(stored)
            del updated[key]
            records = json.dumps(updated)
            item = api.content.get(UID=uuid)
            setattr(item, field_name, records)
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

