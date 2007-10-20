import logging, StringIO
import cssutils

mylog = StringIO.StringIO()
logging.basicConfig(stream=mylog) # here loglevel is not set

cssutils.log.setlog(logging.getLogger('mylog')) 
cssutils.log.setloglevel(logging.DEBUG)
 
sheet = cssutils.parseString('a { x: 1; } @import "x";')
print '--- customlog content  ---'
print mylog.getvalue()

# OUTPUTS:
#--- customlog content  ---
#INFO:mylog:Property: No CSS2 Property: "x".
#INFO:mylog:CSSValue: Unable to validate as no or unknown property context set for
# this value: u'1'
#ERROR:mylog:CSSStylesheet: CSSImportRule not allowed here. [1:13: @import]

