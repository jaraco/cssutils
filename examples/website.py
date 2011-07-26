"""website example tests

Log output cannot be tested!

#doctest: +ELLIPSIS

"""
import cssutils
cssutils.ser.prefs.useDefaults()

def profile():
    """
    >>> import cssutils
    >>> sheet = cssutils.parseString('x { -test-custommacro: x }')
    >>> print sheet.cssRules[0].style.getProperties()[0].valid
    False
    >>> M1 = {
    ...      'testvalue': 'x'
    ...      }
    >>> P1 = {
    ...    '-test-tokenmacro': '({num}{w}){1,2}',
    ...    '-test-macro': '{ident}|{percentage}',
    ...    '-test-custommacro': '{testvalue}',
    ...    # custom validation function
    ...    '-test-funcval': lambda(v): int(v) > 0
    ...      }
    >>> cssutils.profile.addProfile('test', P1, M1)
    >>> sheet = cssutils.parseString('x { -test-custommacro: x }')
    >>> print sheet.cssRules[0].style.getProperties()[0].valid
    True
    """

def cssparse_example():
    """
    >>> import cssutils, logging
    >>> cssutils.log.setLevel(logging.FATAL)
    >>> sheet = cssutils.parseString('@import url(example.css); body { color: red }')
    >>> # log output not shown
    >>> print sheet.cssText
    @import url(example.css);
    body {
        color: red
        }
    """

def logging():
    """
    >>> import cssutils, logging
    >>> cssutils.log.setLevel(logging.FATAL)
    >>> import logging, StringIO, cssutils
    >>> mylog = StringIO.StringIO()
    >>> h = logging.StreamHandler(mylog)
    >>> h.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    >>> cssutils.log.addHandler(h)
    >>> cssutils.log.setLevel(logging.INFO)
    >>> sheet = cssutils.parseString('a { x: 1; } @import "http://cthedot.de/not-present.css";')
    >>> print mylog.getvalue()
    WARNING Property: Unknown Property name. [1:5: x]
    WARNING HTTPError opening url=http://cthedot.de/not-present.css: 404 Not Found
    WARNING CSSImportRule: While processing imported style sheet href=http://cthedot.de/not-present.css: IOError('Cannot read Stylesheet.',)
    ERROR CSSStylesheet: CSSImportRule not allowed here. [1:13: @import]
    <BLANKLINE>
    """

def prefs():
    """
    >>> import cssutils, logging
    >>> cssutils.log.setLevel(logging.FATAL)
    >>> css = '@import "example.css"; body { color: red }'
    >>> sheet = cssutils.parseString(css)
    >>> cssutils.ser.prefs.indent = 2*' '
    >>> # used to set indentation string, default is 4*' '
    >>> cssutils.ser.prefs.importHrefFormat = 'uri'
    >>> # or 'string', defaults to the format used in parsed stylesheet
    >>> cssutils.ser.prefs.lineNumbers = True
    >>> print sheet.cssText
    1: @import url(example.css);
    2: body {
    3:   color: red
    4:   }
    """


def work_and_build():
    """
    >>> import cssutils, logging
    >>> cssutils.log.setLevel(logging.FATAL)
    >>> cssutils.ser.prefs.useDefaults()
    >>> # --- RESET ---
    >>> from cssutils import css, stylesheets
    >>> sheet = css.CSSStyleSheet()
    >>> sheet.cssText = u'@import url(example.css) tv;'
    >>> print sheet.cssText
    @import url(example.css) tv;
    >>> style = css.CSSStyleDeclaration()
    >>> style['color'] = 'red' # until 0.9.5: setProperty(u'color', u'red')
    >>> stylerule = css.CSSStyleRule(selectorText=u'body', style=style)
    >>> sheet.add(stylerule) # use this from 0.9.5 which always succeeds
    1
    >>> # OR THIS IS THE OFFICIAL DOM METHOD IF YOU WANT TO USE IT:
    >>> # sheet.insertRule(stylerule, 0) # try before @import
    >>> # xml.dom.HierarchyRequestErr: CSSStylesheet: Found @charset, @import or @namespace before index 0.
    >>> # sheet.insertRule(stylerule) # at end of rules, returns index
    >>> print sheet.cssText
    @import url(example.css) tv;
    body {
        color: red
        }
    >>> # returns if new Medium is wellformed and has been added
    >>> sheet.cssRules[0].media.appendMedium('print')
    True
    >>> # returns the new Selector:
    >>> sheet.cssRules[1].selectorList.appendSelector('a')
    cssutils.css.Selector(selectorText=u'a')
    >>> print sheet.cssText
    @import url(example.css) tv, print;
    body, a {
        color: red
        }
    """

def api_addons():
    """
    >>> import cssutils, logging
    >>> cssutils.log.setLevel(logging.FATAL)
    >>> cssText = '''background: white url(paper.png) scroll; /* for all UAs */
    ... background: white url(ledger.png) fixed; /* for UAs that do fixed backgrounds */
    ... '''
    >>> # omit comments for this example
    >>> cssutils.ser.prefs.keepComments = False
    >>> style = cssutils.css.CSSStyleDeclaration(cssText=cssText)
    >>> print style.cssText
    background: white url(paper.png) scroll;
    background: white url(ledger.png) fixed;
    >>> # work with properties:
    >>> proplist = style.getProperties('background', all=True)
    >>> proplist
    [cssutils.css.Property(name='background', value=u'white url(paper.png) scroll', priority=u''), cssutils.css.Property(name='background', value=u'white url(ledger.png) fixed', priority=u'')]
    >>> for prop in proplist: print prop.value
    white url(paper.png) scroll
    white url(ledger.png) fixed
    >>> # overwrite the current property, to overwrite all iterate over proplist
    >>> style['background'] = ('red', '!important')
    >>> # importance in DOM ist 'important' but '!important' works too
    >>> print style['background'], style.getPropertyPriority('background')
    red important
    >>> print style.cssText
    background: white url(paper.png) scroll;
    background: red !important;
    >>> # output only "effective" properties
    >>> cssutils.ser.prefs.keepAllProperties = False
    >>> print style.cssText
    background: red !important;
    """

if __name__ == '__main__':
    import doctest
    doctest.testmod()
