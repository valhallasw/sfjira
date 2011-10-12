import sys
import parser
import codecs

if len(sys.argv) != 3 or sys.argv[1] == "--help":
    print "%s <export.xml> <config.py>"
    print ""
    print "JIRA conversion, stage 1: preparation"
    print "Writes bare configuration file to allow CSV export"
    sys.exit()


issues = parser.get_issues(sys.argv[1])
outfile = sys.argv[2]

counts = {}
get_values = ['priority', 'status', 'resolution', 'artifact_type', 'category', 'artifact_group_id']
get_values = dict([(i, set()) for i in get_values])
max_comments = 0
max_attachments = 0

print "Parsing issues...", 
n=0
for issue in issues:
    for key, s in get_values.iteritems():
        s.update([issue[key]])
    for key in issue.fields:
        counts[key] = counts.setdefault(key, 0) + 1
    max_comments = max(max_comments, len(issue.artifact_messages))
    max_attachments = max(max_attachments, len(issue.attachments))
    n=n+1
    if n%100 == 0:
        print n,

print "DONE"

print "Writing to %s..." % outfile,
f = codecs.open(outfile, "w", "utf-8")
print >> f, "# -*- coding: utf-8 -*- "
print >> f, "# configuration file for JIRA export (python format)"
print >> f, "# only the project id and bugtracker ids have to be set"
print >> f, "# you can get them from the sf.net of the bug trackers: "
print >> f, "# http://sourceforge.net/tracker/?atid=<tracker id>&group_id=<project id>&func=browse"
print >> f, ""
print >> f, "project_id = # <project id>"
print >> f, ""

print >> f, "artifact_ids = {}"
for artifact_key in get_values['artifact_type']:
    print >> f, "artifact_ids[%r] = # <%s tracker id>" % (artifact_key, artifact_key)

print >> f, ""
print >> f, "# END OF CONFIGURATION"
print >> f, ""
print >> f, "max_comments = %r" % max_comments
print >> f, "max_attachments = %r" % max_attachments
print >> f, "get_values = %r" % get_values
print >> f, "counts = %r" % counts

print "DONE"
