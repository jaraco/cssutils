"""combines sheets referred to by @import rules in a given CSS proxy sheet
into a single new sheet.

- proxy currently is a path (no URI!)
- in @import rules only relative paths do work for now but should be used
  anyway
- currently no nested @imports are resolved
- messages are send to stderr
- output to stdout.

Example::

    csscombine sheets\csscombine-proxy.css -m -t ascii -s utf-8
        1>combined.css 2>log.txt

results in log.txt::

    COMBINING sheets\csscombine-proxy.css
    USING SOURCE ENCODING: utf-8
    * PROCESSING @import sheets\csscombine-1.css
    * PROCESSING @import sheets\csscombine-2.css
    SETTING TARGET ENCODING: ascii

and combined.css::

    @charset "ascii";a{color:green}body{color:#fff;background:#000}

or without option -m::

    @charset "ascii";
    /* proxy sheet which imports sheets which should be combined \F6 \E4 \FC  */
    /* @import "csscombine-1.css"; */
    /* combined sheet 1 */
    a {
        color: green
        }
    /* @import url(csscombine-2.css); */
    /* combined sheet 2 */
    body {
        color: #fff;
        background: #000
        }

TODO
    - URL or file hrefs? URI should be default
    - no nested @imports are resolved yet
    - maybe add a config file which is used?

"""
__all__ = ['csscombine']
__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import os
import sys
import cssutils
from cssutils.serialize import CSSSerializer

def csscombine(proxypath, sourceencoding=None, targetencoding='utf-8',
               minify=True):
    """
    :returns: combined cssText
    :Parameters:
        `proxypath`
            url or path to a CSSStyleSheet which imports other sheets which
            are then combined into one sheet
        `sourceencoding`
            encoding of the source sheets including the proxy sheet
        `targetencoding`
            encoding of the combined stylesheet, default 'utf-8'
        `minify`
            defines if the combined sheet should be minified, default True
    """
    sys.stderr.write('COMBINING %s\n' % proxypath)
    
    if sourceencoding is not None:
        sys.stderr.write('USING SOURCE ENCODING: %s\n' % sourceencoding)
        
    src = cssutils.parseFile(proxypath, encoding=sourceencoding)
    srcpath = os.path.dirname(proxypath)
    r = cssutils.css.CSSStyleSheet()
    for rule in src.cssRules:
        if rule.type == rule.IMPORT_RULE:
            fn = os.path.join(srcpath, rule.href)
            sys.stderr.write('* PROCESSING @import %s\n' % fn)
            importsheet = cssutils.parseFile(fn, encoding=sourceencoding)
            importsheet.encoding = None # remove @charset
            r.insertRule(cssutils.css.CSSComment(cssText=u'/* %s */' %
                                                 rule.cssText))
            for x in importsheet.cssRules:
                if x.type == x.IMPORT_RULE:
                    sys.stderr.write('INFO\tNested @imports are not resolved: %s\n' % x.cssText)

                r.add(x)

        else:
            r.insertRule(rule)

    sys.stderr.write('SETTING TARGET ENCODING: %s\n' % targetencoding)
    r.encoding = targetencoding
    if minify:
        # save old setting and use own serializer
        oldser = cssutils.ser
        cssutils.setSerializer(CSSSerializer())
        cssutils.ser.prefs.useMinified()
        cssText = r.cssText
        cssutils.setSerializer(oldser)
    else:
        cssText = r.cssText
    return cssText

def main(args=None):
    import optparse

    usage = "usage: %prog [options] path"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-s', '--sourceencoding', action='store',
        dest='sourceencoding', default='css',
        help='encoding of input, defaulting to "css". If given overwrites other encoding information like @charset declarations')
    parser.add_option('-t', '--targetencoding', action='store',
        dest='targetencoding',
        help='encoding of output, defaulting to "UTF-8"', default='utf-8')
    parser.add_option('-m', '--minify', action='store_true', dest='minify',
        default=False,
        help='saves minified version of combined files, defaults to False')
    options, path = parser.parse_args()

    if not path:
        parser.error('no path given')
    else:
        path = path[0]

    print csscombine(path, options.sourceencoding, options.targetencoding,
                     options.minify)


if __name__ == '__main__':
    sys.exit(main())