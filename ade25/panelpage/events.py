import json
from five import grok
from zope.lifecycleevent import modified

from plone.uuid.interfaces import IUUID
from zope.container.interfaces import IObjectAddedEvent
from ade25.panelpage.contentblock import IContentBlock


@grok.subscribe(IContentBlock, IObjectAddedEvent)
def setDefaultContentBlockLayout(obj, event):
    current = getattr(obj, 'contentBlockLayout', list())
    if not current:
        updated = list()
    else:
        updated = json.loads(current)
    col = {
        'uuid': IUUID(obj),
        'component': u"placeholder",
        'grid-col': 12
    }
    updated.append(col)
    setattr(obj, 'contentBlockLayout', json.dumps(updated))
    modified(obj)
    obj.reindexObject(idxs='modified')
