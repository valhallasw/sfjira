import sys
import parser
import codecs

if len(sys.argv) < 3 or len(sys.argv) > 4 or sys.argv[1] == "--help":
    print "%s <export.xml> <config.py> [base_config]"
    print ""
    print "JIRA conversion, stage 1: preparation"
    print "Writes bare configuration file to allow CSV export"
    print "Base values for configuration file can be read from [base_config]"
    sys.exit()

if len(sys.argv) == 4:
    base_config = __import__(sys.argv[3].split('.py')[0])
    base_project_id = base_config.project_id
    base_tracker_ids = base_config.tracker_ids
    base_date_format = base_config.date_format
    print "Successfully imported %s" % sys.argv[3]
else:
    base_project_id = None
    base_tracker_ids = {}
    base_date_format = "%d %B %Y %H:%M:%S"

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
print >> f, "project_id = %r # <project id>" % base_project_id
print >> f, ""

print >> f, "tracker_ids = {}"
for artifact_key in get_values['artifact_type']:
    print >> f, "tracker_ids[%r] = %r # <%s tracker id>" % (artifact_key, base_tracker_ids.get(artifact_key, None), artifact_key)

print >> f, ""
print >> f, "date_format = %r" % base_date_format
print >> f, ""
print >> f, "# END OF CONFIGURATION"
print >> f, ""
print >> f, "max_comments = %r" % max_comments
print >> f, "max_attachments = %r" % max_attachments
print >> f, "get_values = %r" % get_values
print >> f, "counts = %r" % counts
print >> f, "source = %r" % sys.argv[1]

print "DONE"
