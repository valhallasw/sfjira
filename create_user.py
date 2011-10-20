import sys
import ucsv
import parser

if len(sys.argv) != 3 or sys.argv[2] == '--help':
    print "%s <config.py> <create_user.csv>"
    print ""
    print "Conversion stage 2 -- user creation output"
    sys.exit()

config = __import__(sys.argv[1].split(".py")[0])
writer = ucsv.UnicodeWriter(sys.argv[2])

print "sf.net -> JIRA conversion, pass 2...",

import config
header = [u"summary", u"submitter"]
writer.writerow(header)

for user in config.usernames:
    writer.writerow([u"Creating user %r" % user, user])
