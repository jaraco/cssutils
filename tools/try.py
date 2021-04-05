import cssutils
import logging
import os
import sys
import timeit
import urllib.request
import urllib.error
import urllib.parse
import xml
import xml.dom

sys.stdout.write(sys.version)
print()


def save(name, string):
    f = open(name, 'w')
    f.write(string)
    f.close()


def maketokens(valuelist):
    # returns list of tuples
    return [('TYPE', v, 0, 0) for v in valuelist]


if 1:
    # m = cssutils.stylesheets.MediaList(
    #     'tv and (color), handheld and (width: 1px) and (color)')
    # m[10] = 'tv'
    # print m.mediaText

    css = '''
    :root {
  var-theme-colour-1: #009EE0;
  var-theme-colour-2: #FFED00;
  var-theme-colour-3: #E2007A;
  var-spacing: 24px;
}
        a {
            bottom: var(b, x);
            color: var(theme-colour-1, rgb(14,14,14));
            left: var(L, 1px);
            z-index: var(L, 1);
            top: var(T, calc( 2 * 1px ));
            background: var(U, url(example.png));
            border-color: var(C, #f00)
        }
    '''
    print(cssutils.parseString(css).cssText)

    sys.exit(1)


if 1:
    css = '''@media all and (width: 10px), all and (height:20px) {
        a {color:red}
    }
    '''
    css = '''@media (min-device-pixel-ratio: 1.3), (min-resolution: 1.3dppx){
        a {color:red}
    }'''
    css = '''@media not handheld/**/,/**/ all/**/and/**/ (/**/width: 10px) and (color), tv/**/{
        a {color:red}
    }'''
    css = '''@media tv,braille,tv {
        a {color:red}
    }'''
    # print cssutils.parseString(css).cssText
    # sys.exit(1)

    # m = cssutils.stylesheets.MediaList('not tv,braille and')
    m = cssutils.stylesheets.MediaList('(color),braille and, tty')

    print()
    print(m, m.wellformed)
    print(m.mediaText)
    print(m.length)
    for mq in m:
        print(mq, mq.mediaType)
    # print
    # for mq in m:
    #    mq.mediaType = 'tv'
    #    print mq.mediaType, mq

    # mq = cssutils.stylesheets.MediaQuery('tv,')
    # print mq
    # print mq.mediaText

    sys.exit(1)


if 1:
    # @media (min-device-pixel-ratio: 1.3), (min-resolution: 1.3dppx) {
    css = '''@media all and (min-width:1px), (max-width: 2px) {
  .logo {
    background-color: blue;
  }
}
'''
    print(cssutils.parseString(css).cssText)

    sys.exit(1)

if 1:
    css = 'matrix(0.000092, 0.250000, -0.250000, 0.000092, 0, 0); }'
    p = cssutils.css.Property('transform', css)
    print(p)
    print()
    pv = p.propertyValue
    for c in pv:
        print(c)
        # print c.name, c.colorType, c.red, c.green, c.blue, c.alpha
    #    for i, v in enumerate(pv):
    #        print i, v
    #        print 'RGBA', v.red, v.green, v.blue, v.alpha
    #    v = cssutils.css.Value(css)
    # v = cssutils.css.CSSFunction(css)

    #    print v
    #    for i, x in enumerate(v.seq):
    #        print i, x.value
    sys.exit(1)


if 1:
    s = '''
    a {
font-family : a  b;
}
'''
    cssutils.parseString(s).cssText
    sys.exit(1)

    import cssutils

    # remove ALL predefined property profiles
    #    cssutils.profile.removeProfile(all=True)
    #
    # add your custom profile, {num} is defined in Profile and always available
    macros = {'color': 'a|b|c', 'num': '1'}
    props = {'abc': '{num}', 'color': '{color}'}
    cssutils.profile.addProfile('my1', props, macros)

    props2 = {'abc': '{num}'}
    cssutils.profile.addProfile('my2', props2)

    # keep only valid properties (valid in given profile)
    cssutils.ser.prefs.validOnly = True

    print(
        cssutils.parseString(
            '''a {
        color: a;
        background: b;
    }'''
        ).cssText
    )

    cssutils.profile.removeProfile('my1')
    cssutils.profile.removeProfile('my2')

    print(
        cssutils.parseString(
            '''a {
        color: a;
        background: b;
    }'''
        ).cssText
    )

    #    import cssutils, pprint
    #    print "TOKEN_MACROS"
    #    pprint.pprint(cssutils.profile._TOKEN_MACROS)
    #    print "MACROS"
    #    pprint.pprint(cssutils.profile._MACROS)
    #
    #    from cssutils.profiles import macros as predef
    #    from cssutils import profile
    #    macros = {'my-font': predef[profile.CSS_LEVEL_2]['family-name'],
    #              'identifier': predef[profile.CSS_LEVEL_2]['identifier']}
    #    props = {'f': '{my-font}'}
    #    cssutils.profile.addProfile('my-font-profile', props, macros)
    #    print cssutils.parseString('''a {
    #        f: 1; /* 1 is invalid! */
    #        f: Arial;
    #    }''').cssText

    sys.exit(0)


if 1:
    #    v = cssutils.css.CSSVariablesDeclaration()
    #    v.cssText = 'top '
    #    print v
    #
    #    sys.exit(0)
    cssutils.ser.prefs.keepComments = True
    t = '''
    @page x {
        /*1*/
        left: 0;
        @x {}
        /* @ */
        @top-LEFT{
            color: red;
        }
        /*2*/
        top: 0;         /*3*/

        @y;
        color: green;
    }
    '''
    s = cssutils.parseString(t)
    print(s.cssText)

    p = s.cssRules[0]
    print(p)

    sys.exit(1)


if 1:
    sel = [
        'E[foo="bar"], E[foo~="bar"], E[foo^="bar"], E[foo$="bar"], '
        'E[foo*="bar"], E[foo|="bar"]',
        'E:dir(ltr), E:lang(fr), E:any-link, E:local-link, E:local-link(0), '
        'E:target, E:scope',
        'E:not(s1, s2)',
        'E:matches(s1, s2)',
        'E[foo="bar" i]',
        'E /foo/ F',
        '$E > F',
    ]

    #    t = cssutils.tokenize2.Tokenizer()
    #    pprint.pprint(list(t.tokenize(x)))
    #    print

    for i, s in enumerate(sel):
        print(i, s)
        sheet = cssutils.parseString(s + '{color: green}')
        print(sheet.cssText)
        print()

    sys.exit(0)


if 1:
    href = os.path.join(os.path.dirname(__file__), '..', 'sheets', 'import.css')
    href = cssutils.helper.path2url(href)
    # href = 'http://seewhatever.de/sheets/import.css'
    s = cssutils.parseUrl(href, media='tv, print', title='from url')
    print(s.cssText)
    sys.exit(0)


if 1:
    import cssutils.script

    # p = r'sheets\vars\vars.css'
    p = r'sheets\var\start.css'

    do = """
    import cssutils
    t = cssutils.tokenize2.Tokenizer()
    css='''
    @page {}
    @media {}
    @media {}
    @media {}
    @media {}
    @media {}
    @media {}
    /* basic styles
 * $Id$
 */
html,body,h1,h2,h3,h4,h5,h6,p,form,iframe,pre,blockquote,ul,ol,li,dd,dl,fieldset,hr {
    margin: 0;
    padding: 0;
    }
body {
    font: normal 75%/1.5 sans-serif;
    color: #000;
    background-color: #fff;
    }
a {
    text-decoration: none;
    }
img {
    border: 0;
    }
textarea {
    resize: vertical;
    }
*>body sup,
*>body sub {
    vertical-align: baseline;
    position: relative;
    }
    *>body sup {
        top: -0.4em;
        }
    *>body sub {
        bottom: -0.2em;
        }
table {
    border-collapse: collapse;
    border-spacing: 0;
    }
    tr {
        vertical-align: top;
        }
    caption, th {
        text-align: left;
        }
ul, ol, li, dd {
    margin-left:20px
    }
    li {
        line-height: 1.25em;
        }
.inline {
    list-style: none;
    margin-left: 0;
    }
    .inline li {
        display: inline;
        margin-left: 0;
        }
    .inline dt {
        clear: left;
        float: left;
        }
        .inline dd {
            margin-left: 0;
            }

/* useful for and shown by JS */
.jsblock, .jsinline {
    display: none;
    }

/* add to floating elements which shall clear floating after themselves */
* html .clearfix {
    height: 1%; /* IE5-6 */
    }
*+html .clearfix {
    display: inline-block; /* IE7not8 */
    }
.clearfix:after { /* FF, IE8, O, S, etc. */
    content: ".";
    display: block;
    height: 0;
    clear: both;
    visibility: hidden;
    }
    }
    '''
    list(t.tokenize(css))

#    c = {}
#    for x in t.tokenize(css):
#        n = x[0]
#        try:
#            c[n] += 1
#        except KeyError:
#            c[n] = 1
#    print c
    """
    t = cssutils.tokenize2.Tokenizer()

    t = timeit.Timer(do)  # outside the try/except
    try:
        print(t.timeit(100))  # or t.repeat(...)
    except Exception:
        print(t.print_exc())

    #    print cssutils.script.csscombine(p,
    #                                     resolveVariables=True)
    #    cssutils.ser.prefs.resolveVariables = True
    #    s = cssutils.parseFile(p)
    #    print s.cssRules
    #    print s.cssText
    sys.exit(1)


if 1:
    css = '''
    a {
        border: red 1px solid;
        border-radius: 1px  2px /   4px;
        border-top-right-radius: 1%;
        border-top-right-radius: 1% 2%;
        behavior: url(css3pie.htc);
        color: rgba(1,2,3, 0.0);
        margin: 1px 2px 3px;
        padding: 1px 2px;
        background: black;
        background-color: #fff;
        content: "string";
    }
    '''
    t = cssutils.tokenize2.Tokenizer()
    for x in t.tokenize(css):
        print(x)
    #
    #    v = cssutils.css.URIValue(u'url(/**/1)')
    #    print v.cssText
    #    v.uri = 'uri'
    #    print v.cssText
    #    v.value = 'value'
    #    print v.cssText

    sys.exit(1)

if 1:
    # request by Walter
    style = cssutils.parseStyle("background-image: url(1.png), url('2.png')")
    cssutils.replaceUrls(style, lambda url: 'prefix/' + url)
    print(style.cssText)

    sys.exit(1)

if 0:
    # ISSUE 35
    css = (
        """div.one {color: expression("""
        """(function(ele){ele.style.behavior="none";})(this));}   """
    )
    css = (
        """div.one {color: expression(function(ele)"""
        """{ele.style.behavior="none";})(this);}   """
    )
    sheet = cssutils.parseString(css)
    print(sheet.cssText)

    sys.exit(1)


if 1:
    css = """
    .content div:after,
.content div .ieafter { content: ""; position: absolute; z-index: -1;
                        left: 0; top: 0; right: -1px; bottom: -9999px;
                        background: inherit; }

/* IE 6/7/8 fixes */
* html .content       { height: 1%; /* IE6 hasLayout */ }
.content div { -ieafter: expression(this.ieAfter ? 0 : (function(el) {
    el.ieAfter = document.createElement('span'); el.ieAfter.className = 'ieafter';
    el.appendChild(el.ieAfter); })(this)); }
.ieafter { width: expression(parseInt(parentNode.offsetWidth) + 1 + 'px');
    height: expression(parseInt(parentNode.parentNode.offsetHeight) + 'px');
    background-color: expression(parentNode.currentStyle.backgroundColor);
    background-image: expression(parentNode.currentStyle.backgroundImage);
    background-repeat: expression(parentNode.currentStyle.backgroundRepeat); }
                    """
    s = cssutils.parseString(css)
    print(s.cssText)
    sys.exit(1)


if 0:
    # Issue 34
    try:
        raise xml.dom.SyntaxErr('msg')
    except Exception as e:
        print(e)
    sys.exit(1)


if 1:

    def fetcher(url):
        url = url.replace('\\', '/')
        url = url[url.rfind('/') + 1 :]
        return (
            None,
            {
                '3.css': '''
                @variables {
                    over3-2-1-0: 3;
                    over3-2-1: 3;
                    over3-2: 3;
                    over3-2-0: 3;
                    over3-1: 3;
                    over3-1-0: 3;
                    over3-0: 3;
                    local3: 3;
                }

            ''',
                '2.css': '''
                @variables {
                    over3-2-1-0: 2;
                    over3-2-1: 2;
                    over3-2-0: 2;
                    over3-2: 2;
                    over2-1: 2;
                    over2-1-0: 2;
                    over2-0: 2;
                    local2: 2;
                }

            ''',
                '1.css': '''
                @import "3.css";
                @import "2.css";
                @variables {
                    over3-2-1-0: 1;
                    over3-2-1: 1;
                    over3-1: 1;
                    over3-1-0: 1;
                    over2-1: 1;
                    over2-1-0: 1;
                    over1-0: 1;
                    local1: 1;
                }

            ''',
            }[url],
        )

    css = '''
        @import "1.css";
        @variables {
            over3-2-1-0: 0;
            over3-2-0: 0;
            over3-1-0: 0;
            over2-1-0: 0;
            over3-0: 0;
            over2-0: 0;
            over1-0: 0;
            local0: 0;
        }
        a {
            local0: var(local0);
            local1: var(local1);
            local2: var(local2);
            local3: var(local3);
            over1-0: var(over1-0);
            over2-0: var(over2-0);
            over3-0: var(over3-0);
            over2-1: var(over2-1);
            over3-1: var(over3-1);
            over3-2: var(over3-2);
            over2-1-0: var(over2-1-0);
            over3-2-0: var(over3-2-0);
            over3-2-1: var(over3-2-1);
            over3-2-1-0: var(over3-2-1-0);
        }
    '''
    cssutils.ser.prefs.resolveVariables = False
    p = cssutils.CSSParser(fetcher=fetcher)
    s = p.parseString(css)
    # print s.cssText
    print()
    s = cssutils.resolveImports(s)
    print(sorted(s.variables.keys()))

    sys.exit(0)


if 1:
    print(cssutils.ser.prefs.keepUnkownAtRules)
    cssutils.ser.prefs.keepUnkownAtRules = 1
    sys.exit(1)

    def fetcher(url):
        if url == "/1/2.css":
            return (
                None,
                '''@variables {
                color: red;
            }''',
            )
        else:
            return None, 'a { color: red }'

    parser = cssutils.CSSParser(fetcher=fetcher)
    sheet = parser.parseString('''@import "2.css" tv "title";''', href='/1/')

    print(sheet.cssText)

    sys.exit(0)

if 1:
    do = """
    import cssutils
    css = '''
    a {
 color: red;
 background: 1px 2px 3px;
 padding: 1px 1px 2px 5cm;
 font: normal 1px/5em Arial, sans-serif;
 color: red;
 background: 1px 2px 3px;
 padding: 1px 1px 2px 5cm;
 font: normal 1px/5em Arial, sans-serif;
 color: red;
 background: 1px 2px 3px;
 padding: 1px 1px 2px 5cm;
 font: normal 1px/5em Arial, sans-serif;
 color: red;
 background: 1px 2px 3px;
 padding: 1px 1px 2px 5cm;
 font: normal 1px/5em Arial, sans-serif;
 }    '''
    cssutils.parseString(css)
    """
    print(cssutils.VERSION)
    t = timeit.Timer(do)  # outside the try/except
    try:
        print(t.timeit(100))  # or t.repeat(...)
    except Exception:
        print(t.print_exc())

    sys.exit(0)


if 1:

    def f(url):
        return (None, '/*%s*/' % url)

    p = cssutils.CSSParser(fetcher=f)

    cssrulessheet = p.parseString('@import "x";')
    imp = cssutils.css.CSSImportRule(href="imp.css")
    sheet = p.parseString('@charset "ascii";', href='http://example.com')
    sheet.add(cssrulessheet.cssRules[0])
    added = sheet.cssRules[1]
    print(sheet == added.parentStyleSheet)
    print('x' == added.href)
    print(added.styleSheet.encoding)  # == u'utf-8'
    print(1, cssrulessheet.cssText)
    print(2, added.styleSheet.cssText)  # == u'/**/'

    sys.exit(0)


if 0:
    css = '''
    @variables {
      c1: #0f0;
      /*1*/
      c2: red;
      /* TODO @x; */
      a : var(x)
    }
    a {
    color: red}
    '''
    s = cssutils.parseString(css)
    varrule = s.cssRules[0]
    print(varrule)
    for v in varrule.variables:
        print(v, varrule.variables[v])
    print(20 * '-')

    v = cssutils.css.CSSVariablesDeclaration(
        cssText='''
    a: 1px;
    /* 1 */
    c: #f00;
    a: 2px 2px
    '''
    )
    print(v.cssText)
    sys.exit(1)

    v.setVariable('a', '1')
    print(v.getVariableValue('a'))

    print('a' in v)

    v['b'] = 2
    print(v['b'])

    print(v)
    print('keys', list(v.keys()))

    for k in v:
        print(k, v[k])
    for i in range(0, v.length):
        print(i, v.item(i), v.getVariableValue(v.item(i)))

    v.removeVariable('a')
    del v['b']
    print(v)
    print('keys', list(v.keys()))

    sys.exit(0)

if 1:  # noqa: C901
    css = '''
    @variables {
      c1: #0f0;
      c2: scroll;
    }
    @media all {
        a {
            color: var(c1);
            };
    }
    div.logoContainer {
        color:red;
      color: var(c1);
      color: var(c3);
      background: var(c1) no-repeat var(c2) var(c3);
      }
    '''
    s = cssutils.parseString(css)

    varrule, mediarule, stylerule = s.cssRules

    # cssutils.ser.prefs.resolveVariables = True
    print(s.cssText)
    # print 20*'-'
    # print cssutils.resolveVariables(s).cssText

    sys.exit(1)

    print()
    #    p = stylerule.style.getProperty('color')
    #    print p
    #    print '3', id(p.cssValue), type(p.cssValue), p.cssValue
    print('\n--- RESOLVE var() and remove @variables ---')

    # replace vars (ALL!)
    for p in stylerule.style.getProperties(all=True):
        v = p.cssValue
        # print 1, v.cssValueTypeString, v

        if v.cssValueType == v.CSS_VALUE_LIST:
            newvalue = []
            for vi in v:
                if vi.cssValueType == vi.CSS_VARIABLE:
                    if vi.value:
                        print(
                            '+ CSSValueList: Replacing %r with %r' % (p.value, vi.value)
                        )
                        newvalue.append(vi.value)
                    else:
                        print('- CSSValueList: No value found for %r' % vi.cssText)
                        newvalue.append(vi.cssText)
                else:
                    newvalue.append(vi.cssText)

            p.value = ' '.join(newvalue)

        elif v.cssValueType == v.CSS_VARIABLE:
            if v.value:
                print('+ Replacing %r with %r' % (p.value, v.value))
                p.value = v.value
            else:
                print('- No value found for %r' % p.value)

    # remove @variables rules
    for r in s:
        if r.VARIABLES_RULE == r.type:
            s.deleteRule(r)

    # cssutils.ser.prefs.validOnly = True
    print()
    print(s.cssText)

    sys.exit(1)


if 0:
    cssutils.cssproductions.PRODUCTIONS.insert(
        1,
        (
            'EXPRESSION',
            r'\(?\s*function\s*\(({ident},?\s*)*\)\s*\{(\s|\S)*\}\s*\)?'
            r'\((({ident}|\.),?\s*)*\)',
        ),
    )

    css = """
    selector {
x:expression((function(ele){ele.style.behavior=''})(this));
}
    """
    s = cssutils.parseString(css)
    #    p = s.cssRules[0].style.getPropertyCSSValue('x')
    #    print p
    #    p.cssText = u'expression((function(ele){ele.style.behavior="none";})(this))'

    # p = cssutils.css.CSSPrimitiveValue(
    #     u'expression((function(ele){ele.style.behavior="none";})(this))')

    sys.exit(1)


if 1:
    css3 = """
.radius2 {
    border-radius: 3px 6px 8px 10px;
    -moz-border-radius: 3px 6px 8px 10px;
    -webkit-border-radius: 3px 6px 8px 10px;
}
.caption { background: rgba(255, 255, 255, .5); }
.multi-bg {
    background: url(/image/css3-multi-top.png) no-repeat,
    url(/image/css3-multi-bottom.png) no-repeat 0 100%,
    url(/image/css3-multi-repeat.png) repeat-y;
    background-color: #516ac4;
}
.text-shadow {
    text-shadow: 6px 6px 4px #cecece;
    -moz-text-shadow: 6px 6px 4px #cecece;
    -webkit-text-shadow: 6px 6px 4px #cecece;
}
.text-shadow {
    text-shadow: 1px 2px 3px #1a1a1a;
}
.columns {
    -moz-column-count: 3;
    -moz-column-gap: 1em;
    -moz-column-rule: 1px solid black;
    -moz-column-width: 200px;
    -webkit-column-count: 3;
    -webkit-column-gap: 1em;
    -webkit-column-rule: 1px solid black;
    -webkit-column-width: 200px;
}
.border-img {
    background-color: #516ac4;
    border: 10px solid;
    border-image: url(/image/css3-border-img.png) 10 10 10 10 repeat repeat;
    -moz-border-image: url(/image/css3-border-img.png) 10 10 10 10 repeat repeat;
    -webkit-border-image: url(/image/css3-border-img.png) 10 10 10 10 repeat repeat;
}
    """
    print(cssutils.parseString(css3).cssText)
    sys.exit(0)


if 1:
    import cssutils.sac

    echo = cssutils.sac.EchoHandler()
    p = cssutils.sac.Parser(echo)
    p.parseString(
        '''@charset "ascii";
        /* 1 */
        @import url("x");
        @namespace x "urlx";
        @font-face {
            font-family: Test;
            }
        @page {
            margin: 0;
            }
        @media all {
            a{}
            }
        @x 1;
        html, x>y, .x {left:0;color:red ! /*1*/ important;}'''
    )

    print('\n\n--------------')
    print(echo.out)

    sys.exit(1)

    sheet = []
    for t in p.parseString(
        '''
    a, b {
        color: red;
        background: url(/1.png); }'''
    ):
        type_, text, line, col = t
        if 'URI' == type_:
            uri = cssutils.helper.urivalue(text)
            if uri.startswith('/'):
                text = cssutils.helper.uri('..' + uri)

        sheet.append(text)

    print(''.join(sheet))

    sys.exit(1)


if 1:
    s = cssutils.parseString('''a { color: red; top: 0; }''')
    r = s.cssRules[0]
    d = r.style
    print(1, d.color)
    d.color = ''
    print(2, d.color)
    print(s.cssText)

    p = d.getProperty('top')
    print(1, p)
    p.value = ''
    print(2, p)

    sys.exit(0)


if 1:
    css = """
    .heading {
          background: #729FCF -moz-linear-gradient(left top, left bottom,
            from(rgba(255, 255, 255, 0.45)), to(rgba(255, 255, 255, 0.50)),
            color-stop(0.4, rgba(255, 255, 255, 0.25)),
            color-stop(0.6, rgba(255, 255, 255, 0.0)),
            color-stop(0.9, rgba(255, 255, 255, 0.10)));
          color: white;
          height: 40px;
        }
    """
    css = '''
    /* variables and calculations */
    @variables {
      CorporateLogoBGColor: #fe8d12;
      left: 1px;
    }
    div.logoContainer {
      background-color: var(CorporateLogoBGColor);
      /* left: calc(var(left) * 2); */
    }

    /* define declarations to be used in another style declaration
        possible with overriding */
    @define colors {
        color: red;
        background: #fff;
        }
    @define margins {
        top: 1;
        /* left: var(left); */
        }
    a {
        @use colors, margins;
        color: green;
        }

    '''
    s = cssutils.parseString(css)
    print(s.cssText)
    sys.exit(1)

if 1:
    r = cssutils.parseString(
        r'''
        @font-face {
            font-family: a;
            src: local(x)
        }
    '''
    ).cssRules[0]
    print(r, r.valid)
    sys.exit(1)
    for p in st.getProperties():  # noqa
        print(p)
    #        v = p.cssValue
    #        if v.cssValueType == v.CSS_VALUE_LIST:
    #            for i, x in enumerate(v):
    #                #print i, x
    #                #if x.primitiveType == x.CSS_STRING:
    #                #    print '\t', 111, x.getStringValue()
    #                print
    #        print v
    print(st.cssText)  # noqa
    print()
    sys.exit(1)
    s = cssutils.parseString(
        '''
    @font-face {
        src: local(HiraKakuPro-W3), local(Meiryo), local(IPAPGothic);
        src: local(Gentium), url(/fonts/Gentium.ttf);
        src: local(Futura-Medium),
           url(fonts.svg#MyGeometricModern) format("svg");



        src: url(../fonts/LateefRegAAT.ttf) format("truetype-aat"),
             url(../fonts/LateefRegOT.ttf) format("opentype");

        src: url(a) format( "123x"  , "a"   );
        src: local(x);
        src: url(a);
        src: url(../fonts/LateefRegAAT.ttf) format("truetype-aat");
        src: url(DoulosSILR.ttf) format("opentype","truetype-aat");


        }
        /*src: 'x'*/
    /*a {
        font-weight: bolder;
        }
    @page {
        font-weight: bolder;
        }*/
    '''
    )
    for r in s:
        if r.type != r.COMMENT:
            for p in r.style.getProperties(all=True):
                print(p.valid, p)

if 1:
    url = 'http://example.com/test.css'

    def make_fetcher(r):
        # normally r == encoding, content
        def fetcher(url):
            return r

        return fetcher

    sys.exit(0)


def pathname2url(p):
    """OS-specific conversion from a file system path to a relative URL
    of the 'file' scheme; not recommended for general use."""
    # e.g.
    # C:\foo\bar\spam.foo
    # becomes
    # ///C|/foo/bar/spam.foo

    if ':' not in p:
        # No drive specifier, just convert slashes and quote the name
        if p[:2] == '\\\\':
            # path is something like \\host\path\on\remote\host
            # convert this to ////host/path/on/remote/host
            # (notice doubling of slashes at the start of the path)
            p = '\\\\' + p
        components = p.split('\\')
        return urllib.parse.quote('/'.join(components))
    comp = p.split(':')
    if len(comp) != 2 or len(comp[0]) > 1:
        error = 'Bad path: ' + p
        raise IOError(error)

    drive = urllib.parse.quote(comp[0].upper())
    components = comp[1].split('\\')
    path = '///' + drive + '|'
    for comp in components:
        if comp:
            path = path + '/' + urllib.parse.quote(comp)
    return path


if 0:

    def jyhref(path):
        href = os.path.abspath(path)
        href = href.replace('\\', '/')
        return 'file:' + href

    name = os.path.join(os.path.dirname(__file__), '..', 'sheets', 'import.css')

    # href = 'file:' + urllib.pathname2url(name)

    from nturl2path import pathname2url  # noqa

    href = pathname2url(os.path.abspath(name))
    href = href.replace('|', ':')
    href = href[3:]
    href = 'file:' + href

    href = jyhref(name)
    href = None

    print(name, href)
    s = cssutils.parseFile(name, href=href, media='screen', title='from file')

    print(0, s)
    print(1, s.cssRules[0].styleSheet)
    print(2, s.cssRules[0].styleSheet.cssText)
    sys.exit(0)


if 1:
    from cssutils.script import csscombine

    # a = csscombine(url='http://localhost/css.css', targetencoding='iso-8859-1',
    #    minify=False)
    print()
    b = csscombine(
        r"E:\xampp\htdocs\css.css", targetencoding='iso-8859-1', minify=False
    )
    # print a
    print(b)

    sys.exit(0)

if 1:
    css = '''@page :left { @top-left {x:1} left: 0; @top-right {x:1} top: 0}'''
    css = '''@page :left { opacity: 0}'''
    s = cssutils.parseString(css)
    style = s.cssRules[0].style
    print(s.cssText)
    sys.exit(1)


if 1:
    cssutils.log.setLevel(logging.DEBUG)
    css = '''rect(1,2,3)'''
    p = cssutils.css.Property('left', '1.2pc')
    print(p)

    v = cssutils.css.CSSValue(css)
    #
    print(v)
    print(v.cssText)

    #
    # print v.getRGBColorValue()
    # v.setFloatValue(v.CSS_RGBACOLOR, 1)
    print()

    # print v
    # v.setFloatValue(cssutils.css.CSSPrimitiveValue.CSS_KHZ, 2000)
    # print v
    #    s = cssutils.parseString('a { left:  inherit; }')
    #    print s.cssText
    # cssutils.log.raiseExceptions = False
    #    p = cssutils.css.Property(name="color",
    #                              value="red",
    #                              priority="!important"
    #                              )
    #    print p
    #    print p.cssText
    sys.exit(1)


if 1:
    cssutils.log.setLevel(logging.DEBUG)
    s = cssutils.parseString('')
    print(s.cssText)
    # v = s.cssRules[0].style.getPropertyCSSValue('color')
    # print v

    sys.exit()

    from cssutils.profiles import profiles

    # TODO: better API
    #    cssutils.css.profiles.profiles.addProfile('x', {
    #        'color': '1',
    #        'x': '{int}'})
    cssutils.log.setLevel(logging.DEBUG)

    print(list(profiles.propertiesByProfile('profiles.CSS3_COLOR')))

    print(
        cssutils.parseString(
            '''
        a { opacity: 0.9;
            color: #000;
            color: rgba(0,0,0, 0);
        }
    '''
        ).cssText
    )

    sys.exit(1)

if 1:
    cssutils.log.setLevel(logging.DEBUG)
    from cssutils.script import csscombine

    c = csscombine('sheets/csscombine-proxy.css')
    print(c)

    sys.exit(1)


if 0:
    # FETCHER
    def fetchUrlGAE(self):
        """
        uses GoogleAppEngine (GAE)
            fetch(url, payload=None, method=GET, headers={}, allow_truncated=False)

        Response
            content
                The body content of the response.
            content_was_truncated
                True if the allow_truncated parameter to fetch() was True and
                the response exceeded the maximum response size. In this case,
                the content attribute contains the truncated response.
            status_code
                The HTTP status code.
            headers
                The HTTP response headers, as a mapping of names to values.

        Exceptions
            exception InvalidURLError()
                The URL of the request was not a valid URL, or it used an
                unsupported method. Only http and https URLs are supported.
            exception DownloadError()
                There was an error retrieving the data.

                This exception is not raised if the server returns an HTTP
                error code: In that case, the response data comes back intact,
                including the error code.

            exception ResponseTooLargeError()
                The response data exceeded the maximum allowed size, and the
                allow_truncated parameter passed to fetch() was False.
        """
        from google.appengine.api import urlfetch

        try:
            r = urlfetch.fetch(url, method=urlfetch.GET)
        except urlfetch.Error as e:
            cssutils.log.warn(
                'Error opening url=%r: %s' % (url, e.message), error=IOError
            )
        else:
            if r.status_code == 200:
                # find mimetype and encoding
                mimetype = 'application/octet-stream'
                try:
                    import cgi

                    mimetype, params = cgi.parse_header(r.headers['content-type'])
                    encoding = params['charset']
                except KeyError:
                    encoding = None

                return encoding, r.content
            else:
                # TODO: 301 etc
                cssutils.log.warn(
                    'Error opening url=%r: HTTP status %s' % (url, r.status_code),
                    error=IOError,
                )

    def fetcher(url):
        return 'text/css', 'ascii', '/*test*/'

    p = cssutils.CSSParser()  # fetcher=fetcher)
    url = 'http://cdot.local/sheets/import.css'
    x = p.parseUrl(url, encoding='iso-8859-1')
    print()
    print(1, x)
    print(x.cssText[:80])
    print()
    x2 = x.cssRules[2].styleSheet
    print(2, x2)
    print(x2.cssText[:50])

    # ValueError:
    #    css = u'a {content: "ä"}'.encode('iso-8859-1')
    #    s = cssutils.parseString(css, encoding='iso-8859-1')
    #    print s

    # HTTPError
    # _fetchUrl('http://cthedot.de/__UNKNOWN__.css')

    # URLError
    # _fetchUrl('mailto:a.css')
    # _fetchUrl('http://localhost/__UNKNOWN__.css')

    sys.exit(0)


if 0:
    # RESOLVE INDENTATION!!!
    sheet = cssutils.parseString(
        '''
        a,b  { color: red }
        a:hover {color: blue}
        b a { left: 0 }
        c a { color: blue}
        @media all {
            a { color: red;}
            b a { color: blue}
            a:hover { color: blue}
        }
        '''
    )
    sheet.setSerializerPref('indentSpecificities', True)
    print(sheet.cssText)

    sys.exit(0)


if 0:
    # SELECTOR4QUERY
    from lxml.cssselect import CSSSelector

    #    sl = cssutils.css.SelectorList(selectorText='''
    #        :not(a|x) *|* a|* * /*x*/* b>c|c+d[a]~e[a=v].a,
    #        a:not(x) p|a[p|a=a],
    #        [a="x"][a|=dash][a~=incl][a^=pref][a$=suff][a*=suff]''')
    #
    #        #*|*, *|e, |e, e, p|*, p|e   ''')
    s = cssutils.css.Selector('*|* |* * *|a |a a')
    print(s.selectorText)
    ns = [
        {'p': 'URI'},
        {'': 'EMPTY', 'p': 'URI'},
    ]
    for n in ns:
        sl = cssutils.css.SelectorList(
            selectorText='*|* |* * *|a |a a p|* p|a', namespaces=n
        )
        print()
        for s in sl:
            print('ns', n)
            print('Selector.seq:', repr(s.seq))
            print('\t', s.selectorText)
            # print  CSSSelector(s.selectorText).path
            print()

    sys.exit(0)

if 1:
    # QUERY
    defaultsheet = cssutils.parseFile('sheets/default_html4.css')

    css = '''
        a { a: green; /* only here */
            b: red;
            c: green !important; /* important */
            d: red !important;
            e: red !important;
            x: red;
            x: green; /* later */
            }
        body a {
            b: green; /* specificity */
            c: red;
            d: red;
            e: green !important; /* important */
            }
        a { b: green; /* later */
            c: red;
            d: green !important; /* important */
            e: red;
            }
    '''
    css = r'''
        body {
            font: normal 100% sans-serif;
        }
        a {
            font-family: serif;
            c\olor: red;
            font-size: 2em;
        }
        .cssutils {
            font: 1em "Lucida Console", monospace;
            border: 1px solid;
            padding: 0 10px;
        }
    '''
    html = '''<html>
        <body>
            <a href="#1" style="color: green;">link</a>
            <p><a href="#2">coming: <b>b</b>link</a></p>
        </body>
    </html>'''

    from lxml import etree
    from lxml.cssselect import CSSSelector  # noqa

    document = etree.HTML(html)
    e = etree.Element('pre', {'class': 'cssutils'})
    e.text = css
    document.find('body').append(e)

    sheet = cssutils.parseString(css)

    view = {}
    specificities = {}  # temporarily needed
    # TODO: filter rules simpler?, add @media
    rules = (rule for rule in sheet.cssRules if rule.type == rule.STYLE_RULE)

    for rule in rules:
        for selector in rule.selectorList:
            cssselector = CSSSelector(selector.selectorText)
            elements = cssselector.evaluate(document)
            for element in elements:
                # add styles for all matching DOM elements
                if element not in view:
                    # add initial
                    view[element] = cssutils.css.CSSStyleDeclaration()
                    specificities[element] = {}

                for p in rule.style:
                    # update styles
                    if p not in view[element]:
                        view[element].setProperty(p)
                        specificities[element][p.name] = selector.specificity
                    else:
                        sameprio = p.priority == view[element].getPropertyPriority(
                            p.name
                        )
                        if (
                            not sameprio
                            and bool(p.priority)
                            or (
                                sameprio
                                and selector.specificity
                                >= specificities[element][p.name]
                            )
                        ):
                            # later, more specific or higher prio
                            view[element].setProperty(p)
    # pp(view)

    # render somewhat (add @style and text with how it should look
    for element, style in list(view.items()):
        v = style.getCssText(separator='')
        element.set('style', v)
        element.set('title', v)

    f = open('c.html', 'w')
    f.write(etree.tostring(document, pretty_print=True))
    f.close()

    sys.exit(0)


if 1:
    # QUERY
    from lxml.cssselect import CSSSelector

    css = '''@namespace p 'test';
    p|a[att~='1'], b>b, c+c, d d { color: red }'''
    sheet = cssutils.parseString(css)
    for s in sheet.cssRules[1].selectorList:
        print(s)
        print('.prefixes\t', s.prefixes)
        print('.selectorText\t', s.selectorText)
        # new in beta1: needs to be resolved
        print('._items\t\t', list(s.seq._items))
        sel = CSSSelector(s.selectorText)
        print('XPath\t\t', sel.path)
        print()

    sys.exit(0)


if 1:
    # SELECTORS
    s = cssutils.css.SelectorList()
    s.selectorText = 'a,'
    print(repr(s.seq))
    print(s)
    sys.exit(0)

    print('combinator')
    s.selectorText = 'a + b ~ c > d   \n\r e'
    print(s)
    s.selectorText = 'a+b~c>d e'
    print(s)

    print('\n[ type_selector | universal ]')
    s.selectorText = '* |* *|*  *|a b|*'
    print(s)
    print(s.prefixes)
    s.selectorText = 'a |b x|c'
    print(s)
    print(s.prefixes)

    print('\n[ HASH | class | attrib | pseudo | negation ]*')
    s.selectorText = '#a a#b *#c #d'
    print(s)
    s.selectorText = '.a a.b *.c .d'
    print(s)

    print('attrib')
    s.selectorText = 'a[a|href][x="1"][y=a][x*=a][x|=a]'  # ':a x ::b y'
    print(s)

    print('pseudo')
    s.selectorText = '::a x::b a:first-letter b:first-line c:before d:after'
    print(s)
    s.selectorText = ':a(+) :b(-) :c(1em) :d(1) :lang("1" 1) :e(a)'
    print(s)
    s.selectorText = ':a x:a x:a:b'
    print(s)
    s.selectorText = '::a x::a'  # only 1
    print(s)
    print('\nnot(: type_selector | universal | HASH | class | attrib | pseudo)')
    s.selectorText = 'not(a) not(*|*) not(*) not(#a) not(.b) not([a]) not(:d)'
    print(s)

    s.selectorText = '*|* * a|b+|c~a|e#1 #a a.a'  # 'a *~x+b>c'#:not(*)'
    s.selectorText = 'not(*) not(#a) not(.a)'
    print(s)
    print(s.prefixes)
    sys.exit(0)
