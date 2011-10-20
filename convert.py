import sys
import ucsv
import parser

jiradateformat = "%Y%m%d%H%M%S" # javaspeak: yyyyMMddHHmmss

if len(sys.argv) != 3 or sys.argv[2] == '--help':
    print "%s <config.py> <output.csv>"
    print ""
    print "Conversion stage 2 -- csv output"

config = __import__(sys.argv[1].split(".py")[0])
writer = ucsv.UnicodeWriter(sys.argv[2])

print "sf.net -> JIRA conversion, pass 2...",

direct = [u'status', u'submitted_by', u'artifact_group_id', u'summary', u'priority', u'details', u'assigned_to', u'artifact_type', u'category', u'resolution']

header = direct + [u'artifact_history', u"open_date", u"update_date", u"url"] + [u"comment"] * config.max_comments + [u"attachment"] * config.max_attachments
writer.writerow(header)

def setval(row, key, value, offset=0):
    row[header.index(key) + offset] = value

def newrow():
    return [None] * len(header)

for i, issue in enumerate(parser.get_issues(config.source)):
    if i%100 == 0:
        print i,
    if i == 100:
        break
    row = newrow()

    for item in direct:
        setval(row, item, issue[item])

    setval(row, 'artifact_history', u"\n".join([i.__unicode__() for i in issue.artifact_history]))
    setval(row, 'open_date', issue.open_date.strftime(jiradateformat))
    setval(row, 'update_date', issue.artifact_history and max([e.entrydate for e in issue.artifact_history]).strftime(config.date_format))
    setval(row, 'url', 'http://sourceforge.net/tracker/?func=detail&aid=%i&group_id=%i&atid=%i' % (issue.artifact_id, config.project_id, config.tracker_ids[issue.artifact_type]))

    for i, comment in enumerate(issue.artifact_messages):
        # The import docs state:
        # To preserve the comment author/date use format:
        # "05/05/2010 11:20:30; adam; This is a comment."
        # But the plugin source uses the standard yyyyMMddHHmmss format
        # and this seems to work
        setval(row, 'comment', u"%s; %s; %s" % (
            comment.adddate.strftime(jiradateformat), #"%d/%m/%y %H:%M:%S"),
            comment.user_name,
            comment.body), i)

    for i, attachment in enumerate(issue.attachments):
        setval(row, 'attachment', u"http://sourceforge.net/tracker/download.php?group_id=%i&atid=%i&file_id=%i&aid=%i" % (config.project_id, config.tracker_ids[issue.artifact_type], attachment, issue.artifact_id))

    writer.writerow(row)
