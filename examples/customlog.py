import logging
import StringIO

import cssutils

# init custom log
customlog = StringIO.StringIO()
logging.basicConfig(stream=customlog)

# set log
cssutils.log.setlog(logging.getLogger())

# try
sheet = cssutils.parseString('a { x: 1; } @import "x";')
print '--- customlog content  ---'
print customlog.getvalue()

# set new log level and try again
cssutils.log.setloglevel(logging.DEBUG)
sheet = cssutils.parseString('a { x: 1; } @import "x";')
print '--- customlog content level DEBUG ---'
print customlog.getvalue()
