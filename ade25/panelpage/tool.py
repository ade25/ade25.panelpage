# -*- coding: utf-8 -*-
"""Module providing genearal toolset for panel management"""
import datetime
import json
import uuid as uuid_tool

import time

from Products.CMFPlone.utils import safe_unicode
from five import grok
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getUtility
from zope.interface import Interface
from zope.lifecycleevent import modified
from zope.schema import getFieldsInOrder
# from collective.beaker.interfaces import ISession

SESSION_KEY = 'Uh53dAfH2JPzI/lIhBvN72RJzZVv6zk5'


class PanelTool(object):
    """ Utility providing CRUD operation for panel pages """

    def create(self, uuid=None, data=None):
        item = api.content.get(UID=uuid)
        start = time.time()
        initial_data = self.create_record(uuid, item, data)
        end = time.time()
        initial_data.update(dict(_runtime=str(end-start)))
        json_data = json.dumps(initial_data)
        setattr(item, 'panelLayout', json_data)
        modified(item)
        item.reindexObject(idxs='modified')
        return json_data

    # @memoize
    def read(self, uuid, key=None):
        item = api.content.get(UID=uuid)
        stored = getattr(item, 'panelLayout', None)
        data = dict()
        if stored is not None:
            data = json.loads(stored)
        if key is not None:
            records = data['items']
            data = records[int(key)]
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

    def delete(self, uuid, key=None):
        stored = self.read(uuid)
        if key is not None:
            stored[key] = dict()
            updated = json.dumps(stored)
            item = api.content.get(UID=uuid)
            setattr(item, 'panelLayout', updated)
            modified(item)
            item.reindexObject(idxs='modified')
        return uuid

    def create_record(self, uuid=None, item=None, data=None):
        record_uid = uuid_tool.uuid4()
        if uuid:
            record_uid = uuid
        record_title = str(uuid_tool.uuid4())
        if item:
            record_title = item.Title()
        records = {
            "id": str(uuid_tool.uuid4()),
            "uid": str(record_uid),
            "timestamp": str(int(time.time())),
            "_runtime": "0.0000059604644775390625",
            "created": datetime.datetime.now().isoformat(),
            "title": record_title,
            "items": []
        }
        # Add potential initial data
        if data:
            records['items'].append(data)
        return records

    def safe_encode(self, value):
        """Return safe unicode version of value.
        """
        su = safe_unicode(value)
        return su.encode('utf-8')

