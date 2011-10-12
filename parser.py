import codecs

from datetime import datetime
from xml.dom.pulldom import START_ELEMENT, parse

class SFObject(object):
    def __init__(self, node):
        self.fields = []
        for field in node.childNodes:
            if field.nodeName != 'field':
                continue
            name = field.getAttribute('name')
            value = (field.firstChild and field.firstChild.wholeText) or u""

            # sf.net stores data as htmlentities of windows-1252-decoded utf-8. Or something like that, it's not really
            # clear. It's crap, anyway. This seems to reproduce the results on sf.net itself...
            value = value.encode('windows-1252', 'ignore').decode('utf-8', 'replace')

            value = self._parse_value(field, name, value)
           
            if value in ["nobody", "None", ""]:
                value = None
            setattr(self, name, value)
            self.fields.append(name)

        self._after_parse()

    def _parse_value(self, field, name, value):
        return value

    def _after_parse(self):
        pass

    def _setifnotset(self, field, value):
        if field not in self.fields:
            setattr(self, field, value)

    def __getitem__(self, value):
        return getattr(self, value)

    def __repr__(self):
        return "<" + unicode(self).encode('ascii', 'replace') + ">"


class Artifact(SFObject):
    def _parse_value(self, field, name, value):
        if name == "priority" or name == "artifact_id":
            return int(value)
        elif name == "open_date":
            return datetime.utcfromtimestamp(int(value))
        elif name == "artifact_history":    
            return self._parse_history(field)
        elif name == "artifact_messages":
            return self._parse_messages(field)
        return value
    
    def _after_parse(self):
        self._setifnotset("artifact_history", [])
        self._setifnotset("artifact_messages", [])
        self.attachments = dict([(int(hi.old_value.split(":")[0]), hi.old_value.split(":")[1].strip()) for hi in self.artifact_history if hi.field_name == u'File Added'])

        
    
    def _parse_history(self, field):
        return [HistoryItem(node) for node in field.childNodes if node.nodeName == 'history']

    def _parse_messages(self, field):
        return [Message(node) for node in field.childNodes if node.nodeName == 'message']

    def __unicode__(self):
        return u"Artifact #%(artifact_id)i: %(summary)s (%(status)s)" % self

class HistoryItem(SFObject):
    def _parse_value(self, field, name, value):
        if name == "entrydate":
            return datetime.utcfromtimestamp(int(value))
        else:
            return value

    @property
    def entrydate_f(self):
        return self.entrydate.isoformat()

    def __unicode__(self):
        return u"%(mod_by)s changed %(field_name)s (old value: %(old_value)s) at %(entrydate_f)s" % self

class Message(SFObject):
    def _parse_value(self, field, name, value):
        if name == "adddate":
            return datetime.utcfromtimestamp(int(value))
        else:
            return value

    @property
    def adddate_f(self):
        return self.adddate.isoformat()

    def __unicode__(self):
        return u"Message by %(user_name)s at %(adddate_f)s" % self

def get_issues(document):
    doc = parse(document)
    for event, node in doc:
        if event == START_ELEMENT and node.localName == "artifact":
            doc.expandNode(node)
            yield Artifact(node)


                
