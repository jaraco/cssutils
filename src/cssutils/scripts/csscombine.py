"""resolves imports in a given CSS proxy sheet

issues
- URL or file hrefs? URI should be default and therefor baseURI is needed
- no nested @imports are resolved yet
- namespace rules are not working yet!
    - @namespace must be resolved (all should be moved to top of main sheet?
      but how are different prefixes resolved???)

"""
import os
import sys
import cssutils

def combine(proxy, srcenc='css', tarenc='utf-8', minified=True):
    """
    TODO:
    
    - encoding
    - read conf
    """
    src = cssutils.parse(proxy, encoding=srcenc)
    sys.stderr.write('COMBINING %s\n' % proxy)
    srcpath = os.path.dirname(proxy)
    r = cssutils.css.CSSStyleSheet()
    for rule in src.cssRules:
        if rule.type == rule.IMPORT_RULE:
            fn = os.path.join(srcpath, rule.href)
            sys.stderr.write('* PROCESSING @import %s\n' % fn)
            importsheet = cssutils.parse(fn, encoding=srcenc)
            importsheet.encoding = None # remove @charset
            r.insertRule(cssutils.css.CSSComment(cssText=u'/* %s */' % 
                                                 rule.cssText))
            for x in importsheet.cssRules:
                if x.type == x.IMPORT_RULE:
                    sys.stderr.write('WARN\tNo nested @imports: %s\n' % x.cssText)
                # TODO: too simple if prefixes different in sheets!
#                elif x.type == x.NAMESPACE_RULE:
#                    print 'INFO\tMoved to begin of sheet', x.cssText
#                    r.insertRule(x, 0)   
                else:
                    r.insertRule(x)   
            #r.insertRule(importsheet.cssRules)
            
#        elif rule.type == rule.NAMESPACE_RULE:
#            print 'INFO\tMoved to begin of sheet', rule.cssText
#            r.insertRule(rule, 0)   
        else:
            r.insertRule(rule)
            
    r.encoding = tarenc
    if minified:
        cssutils.ser.prefs.useMinified()
    return r.cssText     
    

def main(args=None):
    import optparse

    usage = "usage: %prog [options] URL"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-s', '--srcenc', action='store', dest='srcenc',
                      default='css',
        help='encoding of input, defaulting to "css". If given overwrites other encoding information like @charset declarations')
    parser.add_option('-t', '--tarenc', action='store', dest='tarenc',
        help='encoding of output, defaulting to "UTF-8"', default='utf-8')
    parser.add_option('-m', '--minified', action='store_true', dest='minified',
        help='saves minified version of combined files, defaults to False')
    options, url = parser.parse_args()
    
    if not url:
        parser.error('no URL given')
    else:
        url = url[0]
       
    print combine(url, options.srcenc, options.tarenc, options.minified)


if __name__ == '__main__':
    sys.exit(main())