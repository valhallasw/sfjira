import codecs

from datetime import datetime
from xml.dom.pulldom import START_ELEMENT, parse

class Artifact(object):
    def __init__(self, node):
        for field in node.childNodes:
            if field.nodeName != 'field':
                continue
            name = field.getAttribute('name')
            value = (field.firstChild and field.firstChild.wholeText) or u""

            # sf.net stores data as htmlentities of windows-1252-decoded utf-8. Or something like that, it's not really
            # clear. It's crap, anyway. This seems to reproduce the results on sf.net itself...
            value = value.encode('windows-1252', 'ignore').decode('utf-8', 'replace')

            if name == "priority" or name == "artifact_id":
                value = int(value)
            elif name == "open_date":
                value = datetime.utcfromtimestamp(int(value))
            elif name == "artifact_history":    
                value = self._parse_history(field)
            elif name == "atifact_messages":
                value = self._parse_messages(field)
            
            if value in ["nobody", "None", ""]:
                value = None
            setattr(self, name, value)

    def _parse_history(self, node):
        return None

    def _parse_messages(self, node):
        return None

    def __unicode__(self):
        return u"Artifact #%(artifact_id)i: %(summary)s (%(status)s)" % self

    def __repr__(self):
        return unicode(self).encode('ascii', 'replace')

    def __getitem__(self, value):
        return getattr(self, value)

class HistoryItem(object):
    pass

class Message(object):
    pass

def get_issues(document):
    doc = parse(document)
    for event, node in doc:
        if event == START_ELEMENT and node.localName == "artifact":
            doc.expandNode(node)
            yield Artifact(node)


                
