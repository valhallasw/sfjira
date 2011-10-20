import parser
import codecs

class SFJiraConfigGenerator(object):
    def __init__(self, xml, basefile=None):
        self._xml = xml
        self._issues = parser.get_issues(xml)

        if basefile:
            base_config = __import__(basefile.split('.py')[0])
            self._project_id = base_config.project_id
            self._tracker_ids = base_config.tracker_ids
        else:
            self._project_id = None
            self._tracker_ids = {}

    def parse(self):
        self.counts = {}

        get_values = ['priority', 'status', 'resolution', 'artifact_type', 'category', 'artifact_group_id']
        self.get_values = dict([(i, set()) for i in get_values])
        self.max_comments = 0
        self.max_attachments = 0

        self.usernames = set()

        print "Parsing issues...", 
        n=0
        for n, issue in enumerate(self._issues):
            for key, s in self.get_values.iteritems():
                s.update([issue[key]])
            for key in issue.fields:
                self.counts[key] = self.counts.setdefault(key, 0) + 1
            self.max_comments = max(self.max_comments, len(issue.artifact_messages))
            self.max_attachments = max(self.max_attachments, len(issue.attachments))

            self.usernames.update([issue.assigned_to, issue.submitted_by] + \
                             [m.user_name for m in issue.artifact_messages] + \
                             [h.mod_by    for h in issue.artifact_history])
            if n%100 == 0:
                print n,

        print "DONE"

    def writefile(self, outfile):
        print "Writing to %s..." % outfile,
        f = codecs.open(outfile, "w", "utf-8")
        print >> f, "# -*- coding: utf-8 -*- "
        print >> f, "# configuration file for JIRA export (python format)"
        print >> f, "# only the project id and bugtracker ids have to be set"
        print >> f, "# you can get them from the sf.net of the bug trackers: "
        print >> f, "# http://sourceforge.net/tracker/?atid=<tracker id>&group_id=<project id>&func=browse"
        print >> f, ""
        print >> f, "project_id = %r # <project id>" % self._project_id
        print >> f, ""

        print >> f, "tracker_ids = {}"
        for artifact_key in self.get_values['artifact_type']:
            print >> f, "tracker_ids[%r] = %r # <%s tracker id>" % (artifact_key, self._tracker_ids.get(artifact_key, None), artifact_key)

        print >> f, ""
        print >> f, "# END OF CONFIGURATION"
        print >> f, ""
        print >> f, "max_comments = %r" % self.max_comments
        print >> f, "max_attachments = %r" % self.max_attachments
        print >> f, "get_values = %r" % self.get_values
        print >> f, "usernames = %r" % self.usernames
        print >> f, "counts = %r" % self.counts
        print >> f, "source = %r" % self._xml

        print "DONE"

    def run(self, outfile):
        self.parse()
        self.writefile(outfile)


if __name__=="__main__":
    import sys

    max_args = 3
    sys.argv.extend([None] * max_args)

    cmd, xml, config, base_config = sys.argv[:4]

    if not xml or not config or sys.argv[1] == "--help":
        print "%s <export.xml> <config.py> [base_config.py]"
        print ""
        print "JIRA conversion, stage 1: preparation"
        print "Writes bare configuration file to allow CSV export"
        print "Base values for configuration file can be read from [base_config.py]"
        print "     which is in the same format as the created config.py."
        sys.exit()

    SFJiraConfigGenerator(xml, base_config).run(config)
