import logging, StringIO

EXPOUT = ""
EXPERR = u"Property: Unknown Property name. [1:5: x]\nHTTPError opening url=http://cthedot.de/x: 404 Not Found\nCSSImportRule: While processing imported style sheet href=http://cthedot.de/x: IOError('Cannot read Stylesheet.',)\nCSSStylesheet: CSSImportRule not allowed here. [1:13: @import]\n"

def main():
    import cssutils

    mylog = StringIO.StringIO()
    h = logging.StreamHandler(mylog)
    h.setFormatter(logging.Formatter('%(levelname)s    %(message)s'))
    #cssutils.log.addHandler(h)
    cssutils.log.setLevel(logging.INFO)

    sheet = cssutils.parseString('a { x: 1; } @import "http://cthedot.de/x";')
    #print mylog.getvalue()

    cssutils.log.removeHandler(h)

if __name__ == '__main__':
    main()